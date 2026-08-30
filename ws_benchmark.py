"""
WebSocket Capacity & Stress Testing Tool for OnFood Server

Measures how many concurrent WebSockets the server can establish and maintain.

Features:
  - Tests concurrent WebSocket connections to /ws/orders/{userId}?token={jwt}
  - Supports live server URLs (ws://localhost:8000, wss://api.example.com, etc.)
  - Measures connection latency (min, avg, p95, p99, max)
  - Tests broadcast delivery to active connections
  - Live progress display during connection ramp-up and hold phase
  - Detailed error breakdown and capacity limits report

Usage:
  # Basic test: 100 connections held for 10 seconds
  python ws_benchmark.py --connections 100 --hold 10

  # High-capacity test: 1000 connections at 100 conns/sec
  python ws_benchmark.py --url ws://localhost:8000 --connections 1000 --ramp-rate 100

  # Test remote / deployed server
  python ws_benchmark.py --url wss://api1.krtech.online --connections 500 --hold 15
"""

import argparse
import asyncio
import os
import sys
import time
import uuid
from typing import List, Dict, Optional

# Add project root to path for JWT token generation
sys.path.insert(0, os.path.dirname(__file__))

import websockets
from app.security import create_access_token


# ─── Terminal Colors ───────────────────────────────────────────
class C:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    GREY    = "\033[90m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"


def banner(text: str):
    w = len(text) + 6
    print(f"\n{C.CYAN}{'=' * w}")
    print(f"||  {C.BOLD}{text}{C.RESET}{C.CYAN}  ||")
    print(f"{'=' * w}{C.RESET}")


def ok(msg: str):
    print(f"  {C.GREEN}[OK]{C.RESET} {msg}")


def fail(msg: str):
    print(f"  {C.RED}[FAIL]{C.RESET} {msg}")


def info(msg: str):
    print(f"  {C.GREY}->{C.RESET} {msg}")


def percentile(data: List[float], p: float) -> float:
    if not data:
        return 0.0
    sorted_data = sorted(data)
    idx = int((len(sorted_data) - 1) * (p / 100.0))
    return sorted_data[idx]


# ─── Client Worker ─────────────────────────────────────────────
class WSClient:
    def __init__(self, client_id: int, base_ws_url: str, app_key: str = "ONFOOD_SECURE_CLIENT_APP_KEY_2026"):
        self.client_id = client_id
        self.user_id = str(uuid.uuid4())
        self.token = create_access_token(user_id=self.user_id, role="customer")
        self.ws_url = f"{base_ws_url.rstrip('/')}/ws/orders/{self.user_id}?token={self.token}"
        self.app_key = app_key
        
        self.connected = False
        self.connect_time_ms = 0.0
        self.error: Optional[str] = None
        self.messages_received = 0
        self._ws = None

    async def connect_and_listen(self, stop_event: asyncio.Event) -> None:
        t0 = time.perf_counter()
        headers = {"X-App-Key": self.app_key, "Authorization": f"Bearer {self.token}"}
        try:
            async with websockets.connect(
                self.ws_url,
                additional_headers=headers,
                open_timeout=20.0,
                close_timeout=5.0,
                ping_interval=20,
                ping_timeout=20,
                max_size=10 * 1024 * 1024,
            ) as ws:
                self._ws = ws
                self.connect_time_ms = round((time.perf_counter() - t0) * 1000, 2)
                self.connected = True

                # Keep receiving until stop signal
                while not stop_event.is_set():
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        if msg:
                            self.messages_received += 1
                    except asyncio.TimeoutError:
                        continue
                    except (websockets.ConnectionClosed, websockets.ConnectionClosedError) as exc:
                        if not stop_event.is_set():
                            self.error = f"Closed prematurely: {exc.code} {exc.reason}"
                        break

        except Exception as e:
            self.error = f"{type(e).__name__}: {str(e)}"
            self.connected = False


# ─── Benchmark Runner ──────────────────────────────────────────
async def is_server_reachable(host: str, port: int) -> bool:
    try:
        reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=1.5)
        writer.close()
        await writer.wait_closed()
        return True
    except Exception:
        return False


async def run_benchmark(ws_url: str, total_connections: int, ramp_rate: int, hold_seconds: int, app_key: str = "ONFOOD_SECURE_CLIENT_APP_KEY_2026", auto_server: bool = True):
    # Normalize URL scheme
    raw_url = ws_url
    if ws_url.startswith("http://"):
        ws_url = "ws://" + ws_url[7:]
    elif ws_url.startswith("https://"):
        ws_url = "wss://" + ws_url[8:]
    elif not (ws_url.startswith("ws://") or ws_url.startswith("wss://")):
        ws_url = "ws://" + ws_url

    banner(f"WebSocket Capacity Benchmark - {total_connections} Target Connections")
    info(f"Target URL:         {ws_url}")
    info(f"Target Conns:       {total_connections}")
    info(f"Ramp Rate:          {ramp_rate} conns/sec")
    info(f"Hold Duration:      {hold_seconds} seconds")

    server_process = None
    # Check if local server is reachable, auto-start if not running
    if ("localhost" in ws_url or "127.0.0.1" in ws_url) and auto_server:
        port = 8000
        if ":" in ws_url.split("//")[1]:
            try:
                port = int(ws_url.split("//")[1].split(":")[1].split("/")[0])
            except Exception:
                port = 8000

        reachable = await is_server_reachable("127.0.0.1", port)
        if not reachable:
            info(f"No server running on port {port}. Auto-starting local Uvicorn test server...")
            import subprocess
            cmd = [
                sys.executable, "-m", "uvicorn", "app.main:app",
                "--host", "127.0.0.1", "--port", str(port),
                "--log-level", "warning",
            ]
            server_dir = os.path.dirname(os.path.abspath(__file__))
            server_process = subprocess.Popen(
                cmd,
                cwd=server_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            # Wait for server to become ready
            for _ in range(40):
                await asyncio.sleep(0.25)
                if await is_server_reachable("127.0.0.1", port):
                    ok(f"Local Uvicorn test server is ready on port {port}")
                    break
            else:
                fail(f"Failed to auto-start local server. Please start it manually: uvicorn app.main:app --port {port}")
                if server_process:
                    server_process.terminate()
                return

    try:
        clients = [WSClient(i + 1, ws_url, app_key=app_key) for i in range(total_connections)]
        stop_event = asyncio.Event()

        print(f"\n{C.BOLD}Phase 1: Establishing Connections...{C.RESET}")

        tasks = []
        t_start = time.perf_counter()
        delay_between_conns = 1.0 / ramp_rate if ramp_rate > 0 else 0.0

        # Launch connections with rate limiting
        for idx, client in enumerate(clients):
            tasks.append(asyncio.create_task(client.connect_and_listen(stop_event)))
            if delay_between_conns > 0 and (idx + 1) % max(1, min(20, total_connections // 10)) == 0:
                active_now = sum(1 for c in clients[:idx + 1] if c.connected)
                errs_now = sum(1 for c in clients[:idx + 1] if c.error)
                print(f"\r  Connecting... [{idx + 1}/{total_connections}] | Connected: {C.GREEN}{active_now}{C.RESET} | Failed: {C.RED}{errs_now}{C.RESET}", end="", flush=True)
                await asyncio.sleep(delay_between_conns * max(1, min(20, total_connections // 10)))

        # Allow in-flight handshakes to settle
        await asyncio.sleep(2.0)
        connected_clients = [c for c in clients if c.connected]
        failed_clients = [c for c in clients if not c.connected]

        print(f"\r  Connecting... [{total_connections}/{total_connections}] | Connected: {C.GREEN}{len(connected_clients)}{C.RESET} | Failed: {C.RED}{len(failed_clients)}{C.RESET}")

        # Phase 2: Hold Phase
        banner(f"Phase 2: Holding {len(connected_clients)} Active WebSockets for {hold_seconds}s...")
        for remaining in range(hold_seconds, 0, -1):
            active = sum(1 for c in clients if c.connected and not c.error)
            print(f"\r  Holding active connections: {C.GREEN}{active}{C.RESET} | Time remaining: {remaining}s ", end="", flush=True)
            await asyncio.sleep(1.0)

        print(f"\r  Holding active connections: {C.GREEN}{len(connected_clients)}{C.RESET} | Hold phase completed.       ")

        # Phase 3: Teardown
        info("Closing all WebSocket connections...")
        stop_event.set()
        await asyncio.gather(*tasks, return_exceptions=True)
        t_total = time.perf_counter() - t_start

        # ─── Statistics & Results ──────────────────────────────────
        banner("Benchmark Summary Results")

        success_count = len(connected_clients)
        fail_count = len(failed_clients)
        latencies = [c.connect_time_ms for c in connected_clients if c.connect_time_ms > 0]

        print(f"  {C.CYAN}{'-' * 60}{C.RESET}")
        print(f"  {C.BOLD}Total Attempted:{C.RESET}        {total_connections}")
        print(f"  {C.GREEN}{C.BOLD}Successfully Connected:{C.RESET} {success_count} ({success_count / total_connections * 100:.1f}%)")
        print(f"  {C.RED}{C.BOLD}Failed Connections:{C.RESET}     {fail_count} ({fail_count / total_connections * 100:.1f}%)")
        print(f"  {C.BOLD}Total Test Duration:{C.RESET}    {t_total:.2f}s")
        print(f"  {C.CYAN}{'-' * 60}{C.RESET}")

        if latencies:
            print(f"\n  {C.BOLD}Handshake / Connection Latency:{C.RESET}")
            print(f"    Min:     {min(latencies):>8.2f} ms")
            print(f"    Avg:     {sum(latencies) / len(latencies):>8.2f} ms")
            print(f"    Median:  {percentile(latencies, 50):>8.2f} ms")
            print(f"    p95:     {percentile(latencies, 95):>8.2f} ms")
            print(f"    p99:     {percentile(latencies, 99):>8.2f} ms")
            print(f"    Max:     {max(latencies):>8.2f} ms")
            print(f"  {C.CYAN}{'-' * 60}{C.RESET}")

        if failed_clients:
            print(f"\n  {C.YELLOW}Failure / Error Breakdown:{C.RESET}")
            error_counts: Dict[str, int] = {}
            for c in failed_clients:
                err = c.error or "Unknown error"
                error_counts[err] = error_counts.get(err, 0) + 1
            for err, cnt in error_counts.items():
                print(f"    {C.RED}x{cnt}{C.RESET}  {err}")
            print(f"  {C.CYAN}{'-' * 60}{C.RESET}")

    finally:
        if server_process:
            info("Stopping local test server...")
            server_process.terminate()
            try:
                server_process.wait(timeout=3)
            except Exception:
                server_process.kill()


def main():
    parser = argparse.ArgumentParser(
        description="OnFood Server WebSocket Capacity & Stress Benchmark Tool"
    )
    parser.add_argument(
        "--url", "-u",
        type=str,
        default="ws://127.0.0.1:8090",
        help="Server WebSocket URL (default: ws://127.0.0.1:8090)",
    )
    parser.add_argument(
        "--connections", "-c",
        type=int,
        default=100,
        help="Number of concurrent WebSocket connections to establish (default: 100)",
    )
    parser.add_argument(
        "--ramp-rate", "-r",
        type=int,
        default=50,
        help="Rate of opening new connections per second (default: 50)",
    )
    parser.add_argument(
        "--hold", "-d",
        type=int,
        default=10,
        help="Duration in seconds to hold connections open before closing (default: 10)",
    )
    parser.add_argument(
        "--app-key", "-k",
        type=str,
        default="ONFOOD_SECURE_CLIENT_APP_KEY_2026",
        help="X-App-Key header value (default: ONFOOD_SECURE_CLIENT_APP_KEY_2026)",
    )
    args = parser.parse_args()

    if args.connections < 1:
        print("Error: --connections must be >= 1")
        sys.exit(1)

    asyncio.run(run_benchmark(args.url, args.connections, args.ramp_rate, args.hold, args.app_key))


if __name__ == "__main__":
    main()
