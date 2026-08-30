# Reward Points & Premium — API Changes for App

## Updated Responses (Existing APIs)

### `UserResponse` — login, profile, register all now return:

```json
{
  "id": "...",
  "name": "...",
  "email": "...",
  ...
  "rewardPointsBalance": 0,
  "lifetimePointsEarned": 0,
  "isPremium": false
}
```

| New Field | Type | Description |
|-----------|------|-------------|
| `rewardPointsBalance` | `int` | Current spendable points |
| `lifetimePointsEarned` | `int` | Total points ever earned |
| `isPremium` | `bool` | Premium member or not |

---

### `OrderResponse` — create order, order history, order detail all now return:

```json
{
  "id": "...",
  "totalAmount": 150.00,
  ...
  "pointsEarned": 30
}
```

| New Field | Type | Description |
|-----------|------|-------------|
| `pointsEarned` | `int` | Points earned from this order (0 if not premium) |

---

## New Endpoints

### Student Endpoints (require auth)

---

#### `GET /api/rewards/summary`

Returns points balance and premium status.

**Response:**
```json
{
  "rewardPointsBalance": 450,
  "lifetimePointsEarned": 1200,
  "isPremium": true,
  "premiumExpiresAt": null
}
```

---

#### `GET /api/rewards/history?page=1&limit=20`

Paginated points transaction log. **Requires Premium.**

**Response:**
```json
{
  "transactions": [
    {
      "id": "uuid",
      "orderId": "uuid-or-null",
      "type": "EARNED",
      "points": 30,
      "balanceAfter": 450,
      "description": "Earned 30 points from order",
      "createdAt": "2026-08-24T18:00:00"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 20
}
```

`type` values: `EARNED`, `REDEEMED`, `BONUS`, `REFUNDED`

---

#### `GET /api/rewards/catalog`

Browse available brand coupons. **Requires Premium.** Coupon code is hidden.

**Response:**
```json
[
  {
    "id": "uuid",
    "brandName": "Swiggy",
    "brandLogoUrl": "https://...",
    "title": "₹50 off on Swiggy",
    "description": "Valid on orders above ₹199",
    "pointsCost": 500
  }
]
```

---

#### `POST /api/rewards/claim/{couponId}`

Spend points to claim a coupon. **Coupon code is revealed on success.**

**Response:**
```json
{
  "id": "uuid",
  "brandName": "Swiggy",
  "brandLogoUrl": "https://...",
  "title": "₹50 off on Swiggy",
  "description": "Valid on orders above ₹199",
  "couponCode": "SWIGGY50OFF",
  "pointsCost": 500,
  "claimedAt": "2026-08-24T18:30:00"
}
```

**Error cases:**
- `400` — Not premium
- `400` — Insufficient points
- `404` — Coupon not found or already claimed

---

#### `GET /api/rewards/my-coupons`

All coupons the user has claimed. **Requires Premium.**

**Response:**
```json
[
  {
    "id": "uuid",
    "brandName": "Swiggy",
    "brandLogoUrl": "https://...",
    "title": "₹50 off on Swiggy",
    "description": "Valid on orders above ₹199",
    "couponCode": "SWIGGY50OFF",
    "pointsCost": 500,
    "claimedAt": "2026-08-24T18:30:00"
  }
]
```
