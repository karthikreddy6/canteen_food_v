# OnFood Production Security Improvement Plan

## Purpose and compatibility rules

This document tracks the production-security audit and hardening work for the
FastAPI backend. Every change must preserve:

- Existing API routes and HTTP methods.
- Existing JSON request and response formats.
- `Authorization: Bearer <access_token>` authentication.
- `Content-Type: application/json` and `Accept: application/json` client use.
- Android client compatibility.
- Server-only handling of internal API keys and secrets.

## Update protocol

Before editing an implementation file, add an **In Progress** entry in the
tracking log below. After validation, mark it **Verified** and record the
modified files, security impact, compatibility result, and checks performed.

| Status | Area | Planned work | Evidence / notes |
|---|---|---|---|
| Pending | Audit baseline | Inventory endpoints, middleware, auth, settings, dependencies, static files, SSE, and WebSockets. | |
| Pending | HTTPS and proxy | Add trusted-proxy support, deployment mode settings, and safe HTTPS redirect behavior behind ngrok now and Nginx/Caddy later. Trust `X-Forwarded-*` headers only from the local ngrok agent/proxy. | |
| Pending | Reverse proxy docs | Document the fixed ngrok HTTPS domain, loopback-only Uvicorn upstream, `--proxy-headers`/trusted proxy configuration, HTTP-to-HTTPS behavior, forwarded headers, SSE, WebSockets, HSTS, `X-Content-Type-Options`, and `Referrer-Policy`. | |
| Pending | JWT | Centralize validation; require signature, expiry, issuer, optional audience, algorithm restriction, access-token type, and session/revocation validation. | |
| Pending | Authorization | Ensure authenticated identity always comes from JWT claims and enforce object ownership/roles. | |
| Pending | Real-time APIs | Authenticate SSE and WebSocket order streams; redact compatibility query-token fallback from logs. | |
| Pending | Passwords | Retain bcrypt compatibility; migrate new/changed passwords to Argon2id where safely supported. | |
| Pending | Rate limits | Add Redis-backed limits for login and OTP verification with a development-only local fallback. | |
| Pending | Input validation | Reject unexpected fields, add safe bounds, and enforce request/upload body-size limits without rejecting valid Android payloads. | |
| Pending | Logging | Add structured request logging with request ID, user ID, trusted client IP, endpoint, status, and duration; redact secrets. | |
| Pending | CORS | Replace wildcard credentialed CORS with explicit configured browser origins, methods, and headers. | |
| Pending | Error handling | Keep the existing error JSON shape while returning generic errors for unexpected failures. | |
| Pending | Vendor shutdown | Verify every `/api/vendor/*` endpoint follows the current temporary shutdown policy. | |
| Pending | Dependencies | Scan installed dependencies, pin reviewed versions, and document required upgrades. | |
| Pending | Verification | Run compatibility, authentication, authorization, CORS, proxy, rate-limit, logging-redaction, SSE, and WebSocket tests. | |

## Known findings from initial review

### Critical

- The order WebSocket endpoint currently accepts connections without authenticating the caller; a client can subscribe using another user's ID.

### High

- The customer order-status route needs explicit ownership/role authorization before it can safely modify an order.
- CORS currently permits all origins, methods, and headers while credentials are enabled.
- Application settings include insecure development defaults for critical configuration if production environment variables are absent.
- Unhandled exceptions are returned to clients using raw exception text.
- Request logging records query parameters, which can disclose the SSE query-token compatibility token.
- Disabling the vendor routers does not automatically disable vendor coupon/banner routes registered by the promotions router.

### Medium

- JWT parsing is duplicated across HTTP, SSE, and vendor logic, risking inconsistent validation.
- JWT audience, explicit access-token typing, and centralized revocation checks are absent.
- Login and OTP verification lack dedicated distributed brute-force rate limits.
- The existing IP/account limiter is stored only in process memory and is not suitable for multi-worker production deployments.
- Pydantic request models generally allow unexpected fields unless configured otherwise.
- Logs do not consistently include authenticated user ID or trusted client IP.

### Low

- Current request/response body logging increases the chance of sensitive-data exposure in production logs.
- Docker/PostgreSQL defaults are intended for local development and need production deployment guidance.

### Ngrok reverse-proxy boundary

The current deployment path uses a reserved ngrok HTTPS domain as a temporary
public endpoint. Ngrok terminates public TLS and forwards requests to the local
FastAPI listener. The application must therefore:

- Bind Uvicorn to `127.0.0.1:8000`; never expose the upstream listener directly
  to the internet.
- Enable Uvicorn proxy-header handling only when running behind ngrok, and trust
  forwarded headers only from the local ngrok agent (`127.0.0.1`). Do not trust
  arbitrary client-supplied `X-Forwarded-For`, `X-Forwarded-Host`, or
  `X-Forwarded-Proto` values.
- Validate the configured reserved hostname with an allow-list and reject
  unexpected `Host` headers.
- Treat a request as secure only after trusted proxy-header processing; apply
  HTTPS redirects and HSTS in deployment mode, while retaining plain HTTP for
  local development.
- Preserve streaming behavior through the tunnel: SSE responses must disable
  proxy buffering/timeouts, and WebSocket upgrades must be forwarded and tested
  with `wss://<reserved-domain>`.
- Keep the ngrok authtoken and reserved-domain configuration outside the
  repository; run the agent as a dedicated non-root service on the VPS.
- Ensure the request logger never records bearer tokens, SSE query-token values,
  cookies, or other credentials received through the public endpoint.

Reference startup shape:

```text
Uvicorn: 127.0.0.1:8000 (proxy headers trusted from 127.0.0.1 only)
ngrok:   ngrok http --domain=<reserved-domain> 127.0.0.1:8000
Android: https://<reserved-domain>
WebSocket: wss://<reserved-domain>/ws/orders/{userId}
```

The fixed ngrok address is a temporary deployment bridge. When the VPS receives
its own production domain, replace the tunnel with the VPS reverse proxy while
keeping the same host validation, forwarded-header, HTTPS, streaming, and
logging controls.

## Implementation order

1. Complete inventory and capture the current API compatibility baseline.
2. Secure configuration, ngrok proxy/HTTPS behavior, CORS, request limits, headers, logging, and generic errors.
3. Centralize JWT validation and apply it to HTTP, SSE, and WebSockets.
4. Fix authorization checks and temporarily disabled vendor endpoint coverage.
5. Add rate limiting and password-hash migration support.
6. Add ngrok and reverse-proxy/deployment documentation and dependency scan results.
7. Run regression/security tests and publish the final report below.

## Final security report

Populate after implementation and verification.

### Critical issues

Pending.

### High issues

Pending.

### Medium issues

Pending.

### Low issues

Pending.

### Remaining recommendations

Pending.

## Ngrok deployment verification checklist

- [ ] Reserved ngrok domain is configured through an environment variable and
      no ngrok token is committed to source control.
- [ ] Uvicorn is reachable only on loopback; port `8000` is not publicly open.
- [ ] `GET /` works through the fixed HTTPS domain and direct HTTP is redirected
      or rejected according to deployment mode.
- [ ] Unexpected `Host` headers and untrusted forwarded headers are rejected or
      ignored.
- [ ] API authentication, static assets, SSE, and authenticated `wss` traffic
      work through ngrok.
- [ ] WebSocket user-ID ownership is enforced before accepting a connection.
- [ ] Logs contain request IDs and status data but no JWT, password, OTP, cookie,
      authorization header, or SSE query token.
- [ ] Restarting the Uvicorn and ngrok services restores the same fixed URL.
