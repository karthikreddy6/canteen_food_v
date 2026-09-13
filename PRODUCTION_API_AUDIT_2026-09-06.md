# OnFood API Production Security and Performance Audit

**Date:** 2026-09-06  
**Scope:** FastAPI source, Docker Compose deployment files, environment posture,
all repository Markdown documentation, and read-only public checks of
`https://api1.krtech.online`.

## Executive summary

The public API and Swagger/OpenAPI endpoints are live behind Cloudflare:

- `GET /docs` returned **200 OK**.
- `GET /openapi.json` returned **200 OK**.
- Cloudflare is terminating public TLS and responses include a Cloudflare Ray ID,
  `X-Content-Type-Options`, `Referrer-Policy`, and an application request ID.

The application has solid building blocks: async SQLAlchemy, short-lived access
tokens, refresh-token storage, bcrypt password hashing off the event loop,
rate-limit code, Redis-capable caching, GZip, request IDs, and order query
eager-loading. It is **not yet safe to call production-ready**. The most urgent
risks are exposed Docker ports, a public SQL backup in a static directory,
predictable/demo accounts created at startup, development-mode OTP fallback and
logging behavior, and an insecure production environment mode.

No source or deployment configuration was changed as part of this audit.

## Evidence and limits

This is a read-only audit. The public endpoint checks used ordinary unauthenticated
GET requests only; no login, mutation, brute-force, or ownership tests were
performed. Cloudflare dashboard controls, host firewall rules, the actual running
container state, database contents, and cloudflared service configuration need
server-side confirmation.

## Live non-destructive security checks

The following checks were run against the public API on 2026-09-06. They did not
read response bodies containing customer data, mutate data, enumerate accounts,
or stress the service.

| Check | Result | Assessment |
|---|---|---|
| `GET /api/menu` without `X-App-Key` | `401` | Pass: the app-client gate is enabled for API routes. |
| `GET /api/cart` with valid app key but no Bearer token | `401` | Pass: protected route rejects unauthenticated callers. |
| `GET /api/cart` with valid app key and malformed Bearer token | `401` | Pass: malformed authentication is rejected. |
| `OPTIONS /api/auth/login` with `Origin: https://evil.example` | `400`, no `Access-Control-Allow-Origin` | Pass: untrusted browser origin is rejected. |
| `HEAD /images/onfood_backup.sql` | `404` | Good: the currently deployed endpoint does not expose that file. The source-tree location remains a deployment risk and should still be removed. |
| `POST /` | `405` | Pass: unsupported method is rejected. |
| `GET /` headers | `X-Content-Type-Options` and `Referrer-Policy` present; HSTS, CSP, frame protection, and Permissions-Policy absent | Improvement required. |

These checks do **not** prove all authorization paths are safe. Ownership tests,
rate-limit validation, streaming authentication, vendor-role authorization, and
production-origin firewall verification still need a controlled test plan.

## Findings

| Priority | Finding | Evidence | Risk |
|---|---|---|---|
| Critical | Docker publishes backend and database ports on every host interface. | `docker-compose.yml` maps `8000:8000` and `5432:5432`. | Direct origin/database access can bypass Cloudflare controls if firewall rules permit it. |
| Critical | Database backup is stored inside the public static image directory. | `app/static/images/onfood_backup.sql`; `/images` is mounted by `app/main.py`. | A guessed URL may disclose user data, schema, and password hashes. |
| Critical | Demo accounts are seeded on every application startup, including predictable vendor credentials. | `seed_database()` is called in lifespan; seeded credentials and accounts occur in `app/main.py`. | Anyone who knows a default credential can gain an account or vendor access. |
| Critical | OTP fallback becomes predictable and is returned to clients when WhatsApp delivery fails. OTP values are also written to error logs on send failures. | `app/routers/auth.py`, `create_and_send_otp()` and `send_registration_otp()`. | Account verification/password reset may be bypassed or OTPs leaked into logs. |
| High | Current environment is development mode. | Local `.env` sets `ENVIRONMENT=development`. | HSTS and production log suppression are disabled; response/request bodies containing PII can be logged. |
| High | Client IP trust is unsafe if origin traffic reaches the app directly. | `get_client_ip()` accepts `CF-Connecting-IP` before validating the peer; Compose publishes port 8000. | Attackers can spoof source IP and evade IP-based limits. |
| High | Redis is not configured. | `CACHE_REDIS_URL` is absent. | Rate limiting and cache are per-process only; multiple workers/restarts weaken protections and reduce cache effectiveness. |
| High | API documentation/OpenAPI schema are publicly reachable. | Live `200 OK` responses from `/docs` and `/openapi.json`. | This aids API reconnaissance. Keep public only if intentionally required; otherwise protect with Cloudflare Access. |
| Medium | JWT is decoded separately in SSE code rather than through the central validator. | `app/routers/orders.py`. | Validation behavior can drift; token-version/session status checks can be missed. |
| Medium | JWT query-string fallback is supported for SSE/WebSockets. | `orders.py` and `main.py`. | Tokens can leak via proxies, browser history, analytics, and referrer handling. |
| Medium | Application logging buffers every non-streaming response to log it. | `dev_request_logger` in `app/main.py`. | Extra memory/copying harms latency and throughput, especially for large JSON responses. |
| Medium | The PostgreSQL event bridge opens a new database connection for every notification. | `app/pubsub.py`, `notify()`. | Under order bursts this adds connection churn and latency. |
| Medium | Full menu is cached and then filtered/paginated in Python. | `app/routers/menu.py`. | Menu growth increases memory use, payload work, and query cost. |
| Medium | Documentation and security plan still include ngrok terminology. | `SECURITY_IMPROVEMENT_PLAN.md`, comments in config/main files. | Incorrect proxy assumptions cause deployment mistakes. |
| Low | Dependency versions are broad lower bounds rather than locked, reviewed versions. | `requirements.txt`. | Builds can silently pick changed package releases. |

## Required remediation plan

### Phase 0 — contain exposure immediately

1. Remove `app/static/images/onfood_backup.sql` from the served directory and
   rotate database credentials, JWT secret, OTP secret, app-client key, and all
   exposed/demo account passwords. Treat the backup as exposed until proven
   otherwise.
2. Remove the PostgreSQL host port mapping. It should be available only on the
   Docker network.
3. Bind the backend host mapping to loopback only (`127.0.0.1:8000:8000`), or
   remove it entirely when cloudflared runs as a Compose service on the same
   Docker network.
4. Delete the automatic production seeding path. Put development fixtures in an
   explicit, non-production command that refuses to run in production.
5. Set `ENVIRONMENT=production` and restart only after strong, distinct secrets
   are confirmed. Never put secret values in this document or Git.

### Phase 1 — fix identity and authentication boundaries

1. In production, never return a fallback OTP and never log an OTP. If WhatsApp
   delivery fails, return a generic delivery failure and retry through the
   provider safely.
2. Require a verified trusted proxy peer before honoring `CF-Connecting-IP` or
   `X-Forwarded-For`. Direct requests must use the socket peer address.
3. Centralize JWT validation for HTTP, SSE, and WebSockets. Require signature,
   issuer, expiry, `type=access`, and current token/session version everywhere.
4. Replace query-token streaming authentication with Authorization headers or a
   short-lived, single-use Redis ticket. Do not permit JWTs in URLs in production.
5. Remember that an Android `X-App-Key` is not a secret: it can be extracted
   from the APK. It may be a coarse abuse signal, never an authentication or
   authorization boundary.

### Phase 2 — Cloudflare and origin hardening

1. Run cloudflared as a dedicated service and point it at the internal backend
   service. Do not expose public origin ports.
2. In Cloudflare, enable WAF managed rules, Bot Fight Mode where compatible with
   Android traffic, and rate limits for login, registration, OTP, password reset,
   and college suggestion routes.
3. Restrict `/docs`, `/redoc`, and `/openapi.json` with Cloudflare Access unless
   the public API contract is deliberately public. If public, monitor and rate
   limit them.
4. Enable HSTS at Cloudflare and application level after confirming every
   subdomain supports HTTPS. Add a restrictive CSP for Swagger/static pages and
   a frame-ancestors policy.
5. Use Cloudflare firewall rules to reject traffic that does not come through the
   tunnel; still keep host firewall rules as the primary origin protection.

### Phase 3 — performance and reliability

1. Provision Redis and set `CACHE_REDIS_URL`; require it for production rate
   limits and SSE tickets. Monitor Redis availability and limit failures.
2. Replace response-body logging with metadata-only structured logs in
   production. Emit duration, status, route, request ID, and safely derived user
   ID; do not copy full response bodies.
3. Reuse a PostgreSQL pool/connection for notification publishing, add bounded
   exponential reconnect backoff, and measure reconnect failures.
4. Move menu filtering/pagination/search into SQL with indexes on
   `canteen_id`, availability/visibility, category, and normalized search fields.
   Cache compact endpoint-specific results with bounded keys.
5. Add load testing before scaling: measure p50/p95/p99 latency, error rate,
   PostgreSQL pool saturation, Redis hit ratio, and memory under realistic Android
   menu browsing, login, cart, order, SSE, and WebSocket flows.
6. Pin dependencies using a reviewed lock/constraints file and scan them in CI.

## Android compatibility rules

The remediation must preserve the existing JSON routes and Bearer-token flow.
For Android clients:

- Keep `Authorization: Bearer <access-token>` for protected HTTP calls.
- Store tokens in Android encrypted storage; never add an API key as a trusted
  client identity mechanism.
- Use an authenticated SSE ticket or Authorization-capable WebSocket client,
  not `?token=` URLs.
- Continue retrying transient `429`, `502`, `503`, and `504` failures with
  capped exponential backoff and jitter; do not retry validation failures.
- Preserve `X-Request-Id` in error reports to link client failures to server
  logs without sending passwords, OTPs, or tokens.

## Verification gates

Do not mark the service production-ready until all are demonstrated:

- [ ] External scans cannot connect directly to host ports 5432 or 8000.
- [ ] `/images/onfood_backup.sql` returns 404 and no backups or secrets are in
      static directories, Docker images, volumes, or Git history.
- [ ] Production starts only with non-default secrets and `ENVIRONMENT=production`.
- [ ] Startup does not create demo users/vendors in production.
- [ ] OTP provider failure does not reveal or log an OTP.
- [ ] Spoofed forwarding headers cannot change the logged/rate-limited client IP.
- [ ] Rate limits work consistently across multiple API workers/containers.
- [ ] Expired, wrong-type, revoked, and another-user JWTs are rejected by HTTP,
      SSE, and WebSockets.
- [ ] Order and cart ownership checks reject cross-user access.
- [ ] Load test establishes acceptable p95 latency and no database connection
      exhaustion at expected peak traffic.
- [ ] Cloudflare tunnel, WAF/rate limits, HSTS, logs, backups, and alerts are
      documented in an operational runbook.

## Recommended delivery order

1. Phase 0 containment and credential rotation.
2. Production configuration, Cloudflare/origin boundary, and OTP fixes.
3. Redis plus centralized real-time authentication.
4. Logging/event-bridge/menu performance work.
5. Automated security regression tests, load tests, and release runbook.
