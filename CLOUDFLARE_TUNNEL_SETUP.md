# Cloudflare Tunnel Setup & Hardening Guide for OnFood

This guide explains how to connect your OnFood FastAPI backend to Cloudflare Tunnel for secure, zero-open-port production deployment.

---

## 1. Architecture Overview

```
[ Android App / Web Client ]
             │ (HTTPS / WSS)
             ▼
   [ Cloudflare Edge ] (DDoS Protection, WAF, Bot Fight Mode, SSL)
             │
   [ Cloudflare Tunnel (cloudflared) ] (Encrypted Outbound Tunnel)
             │
             ▼
   [ FastAPI Backend (:8000) ] (Reads CF-Connecting-IP for Rate Limiting)
             │
             ▼
   [ PostgreSQL (:5432) ]
```

---

## 2. Step-by-Step Cloudflare Zero Trust Setup

### Step 1: Create the Tunnel in Cloudflare Dashboard
1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/).
2. Navigate to **Networks** $\rightarrow$ **Tunnels** $\rightarrow$ Click **Add a tunnel**.
3. Choose **Cloudflare (cloudflared)** as the connector $\rightarrow$ Name it (e.g. `onfood-production`).
4. Click **Save tunnel**.

### Step 2: Copy the Tunnel Token
Under the **Install and run a connector** section:
- Look at the Docker or command string. You will see a long token after `--token <YOUR_TOKEN>`.
- Copy that token value.
- Open your `.env` file and set:
  ```ini
  CLOUDFLARE_TUNNEL_TOKEN=eyJhIjoiY2...your_copied_token...
  ```

### Step 3: Configure the Public Hostname Route
In the Cloudflare Tunnel configuration wizard:
1. Go to the **Public Hostname** tab $\rightarrow$ Click **Add a public hostname**.
2. **Public Hostname**:
   - Subdomain: `api` (or whatever you prefer, e.g. `api1`)
   - Domain: `yourdomain.com` (e.g. `krtech.online`)
   - Path: *(leave empty)*
3. **Service**:
   - Type: `HTTP`
   - URL:
     - **If using Docker Compose**: `api:8000` (the internal Docker network service name)
     - **If running directly on host**: `localhost:8000` (or `127.0.0.1:8000`)
4. **Additional Application Settings** (under the same page):
   - **HTTP Settings** $\rightarrow$ Enable **No TLS Verify** (if using self-signed internal TLS) or leave defaults.
   - **Chunked encoding**: `Automatic` (preserves SSE streams).

---

## 3. Cloudflare Edge Hardening & Security Checklist

### 1. Enable WebSockets (Default Enabled)
- In Cloudflare Dashboard $\rightarrow$ **Network** $\rightarrow$ Ensure **WebSockets** is toggled **ON**.
- This enables your live order tracking WebSocket (`/ws/orders/{user_id}`).

### 2. Enable Bot Fight Mode
- Go to **Security** $\rightarrow$ **Bots** $\rightarrow$ Toggle **Bot Fight Mode** to **ON**.
- Automatically blocks malicious scanners, vulnerability bots, and script probes.

### 3. Setup WAF Rate Limiting on Authentication Endpoints
- Go to **Security** $\rightarrow$ **WAF** $\rightarrow$ **Rate Limiting Rules** $\rightarrow$ Click **Create rule**.
- Rule Name: `Rate Limit Auth and OTP`
- If incoming requests match:
  - Field: `URI Path`
  - Operator: `starts with`
  - Value: `/api/auth/`
- Rate limit configuration:
  - Requests: `10`
  - Period: `1 minute`
  - Action: `Block` or `Managed Challenge`
- Click **Deploy**.

### 4. (Optional) Protect API Documentation (`/docs`) with Zero Trust Access
1. In Cloudflare Zero Trust $\rightarrow$ **Access** $\rightarrow$ **Applications** $\rightarrow$ **Add an application**.
2. Type: **Self-hosted**.
3. Application Name: `OnFood Docs Access`.
4. Application Domain: `api.yourdomain.com/docs*`.
5. Add a Policy:
   - Action: `Allow`
   - Include: `Emails ending in @yourcompany.com` or specific admin emails.
6. Now, visitors must pass an email OTP challenge before they can view `/docs` or `/redoc`.

---

## 4. How to Start Everything with Docker Compose

Once your `.env` contains `CLOUDFLARE_TUNNEL_TOKEN`:

```powershell
docker-compose up -d --build
```

To view tunnel logs:
```powershell
docker-compose logs -f tunnel
```

When connected, `cloudflared` will print:
```text
INF Connection registered with Cloudflare edge
```
Your backend is now securely accessible worldwide at `https://api.yourdomain.com` with full DDoS protection, automated SSL, and client IP extraction!
