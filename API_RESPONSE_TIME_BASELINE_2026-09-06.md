# OnFood API Response-Time Baseline

**Target:** `https://api1.krtech.online`  
**Date:** 2026-09-06  
**Method:** One sequential live request per safe endpoint from the test
environment. Times are total client-observed HTTPS durations, including DNS/TLS,
Cloudflare, internet transit, application work, and response transfer.

This is a baseline, not a load test and not an Android device benchmark. Tokens
and credentials were not recorded in this document.

## Results

| Endpoint | Method | Status | Total time (ms) | Response bytes |
|---|---:|---:|---:|---:|
| `/` | GET | 200 | 742.4 | 68 |
| `/docs` | GET | 200 | 742.2 | 1,958 |
| `/openapi.json` | GET | 200 | 540.8 | 74,044 |
| `/api/locations/colleges` | GET | 200 | 693.2 | 351 |
| `/api/locations/canteens` | GET | 200 | 392.2 | 518 |
| `/api/locations/colleges/{id}/canteens` | GET | 200 | 620.3 | 85 |
| `/api/menu/categories` | GET | 200 | 649.5 | 34,087 |
| `/api/menu?canteenId={id}` | GET | 200 | 448.6 | 13,101 |
| `/api/menu/paged?page=1&limit=20&canteenId={id}` | GET | 200 | 421.1 | 7,942 |
| `/api/menu/discounts?canteenId={id}` | GET | 200 | 547.1 | 11,553 |
| `/api/menu/specials?canteenId={id}` | GET | 200 | 486.7 | 401 |
| `/api/menu/search?q=rice&canteenId={id}` | GET | 200 | 509.4 | 2 |
| `/api/menu/category/{id}` | GET | 200 | 666.0 | 1,199 |
| `/api/menu/sync` | GET | 200 | 577.5 | 111,727 |
| `/api/kitchen/status` | GET | 200 | 484.8 | 160 |
| `/api/help/faq` | GET | 200 | 456.6 | 1,279 |
| `/api/cart` | GET | 200 | 497.6 | 42 |
| `/api/banners` | GET | 200 | 442.8 | 259 |
| `/api/orders/history?page=1&limit=10` | GET | 200 | 588.5 | 2,478 |
| `/api/orders/schedule/slots?date=2026-09-06` | GET | 200 | 538.6 | 6,508 |
| `/api/help/tickets` | GET | 200 | 523.6 | 2 |
| `/api/rewards/summary` | GET | 200 | 560.2 | 95 |
| `/api/rewards/history?page=1&limit=20` | GET | 200 | 642.3 | 957 |
| `/api/rewards/catalog` | GET | 200 | 756.5 | 605 |
| `/api/rewards/my-coupons` | GET | 200 | 635.8 | 2 |

## Summary

- Safe endpoints tested: **25**
- Successful responses: **25/25**
- Average total time: **566.6 ms**
- Fastest: **392.2 ms** — `GET /api/locations/canteens`
- Slowest: **756.5 ms** — `GET /api/rewards/catalog`

## Performance interpretation

All endpoints work, but a roughly 400–750 ms single-request baseline is high for
small authenticated/mobile API reads. The timing includes the Cloudflare tunnel
and the remote test path, so application-only latency is not yet known.

Prioritize these measurements next:

1. Add server-side request duration metrics by route, database-query duration,
   connection-pool wait time, Redis hit ratio, and Cloudflare edge timing.
2. Run a concurrent load test from the deployment region and one Android-like
   network profile; record p50, p95, p99, error rate, and saturation points.
3. Reduce large initial payloads: `/api/menu/sync` is 111,727 bytes and menu
   categories are 34,087 bytes in this sample. Use `since` incremental sync,
   pagination, compression, cache headers, and image URLs rather than payload
   expansion.
4. Investigate high-latency routes after server-side timing is available,
   especially rewards catalog, health/docs, college/canteen lookup, category
   listing, rewards history, and menu category.

## Not measured

The remaining operations need dedicated test data or would mutate production
state, so they were intentionally excluded: registration/OTP/password routes,
cart writes, order creation/status changes, ticket creation, reward claims and
subscriptions, account deletion/logout, vendor APIs, SSE/WebSocket streams, and
GET-by-ID routes without an approved disposable order/ticket/coupon fixture.

