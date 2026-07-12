# OnFood Android ↔ Server API Integration Guide

## Base Configuration

```
Base URL      : http://<your-server-ip>:8000
Content-Type  : application/json
Auth Header   : Authorization: Bearer <access_token>
Response Type : JSON (camelCase fields)
```

> All request bodies are JSON. All responses are JSON with camelCase keys.
> Auth-required endpoints return **401 Unauthorized** if token is missing or expired.

---

## 1. Retrofit Setup (Android)

### `ApiClient.kt`
```kotlin
object ApiClient {
    private const val BASE_URL = "http://192.168.x.x:8000/"   // ← your server IP

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor { chain ->
            val token = TokenManager.getToken()                // saved in SharedPreferences
            val request = if (token != null) {
                chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
            } else {
                chain.request()
            }
            chain.proceed(request)
        }
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}
```

---

## 2. Authentication

### 2a. Register
```
POST /api/auth/register
Auth: Not required
```
**Android request body:**
```json
{
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "password": "mypassword123",
  "phone": "9988776655"
}
```
**Success response (201):**
```json
{
  "id": "abc-uuid",
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "phone": "9988776655"
}
```

**Retrofit interface:**
```kotlin
@POST("api/auth/register")
suspend fun register(@Body request: RegisterRequest): Response<UserResponse>
```

---

### 2b. Login
```
POST /api/auth/login
Auth: Not required
```
**Android request body:**
```json
{
  "email": "raj@example.com",
  "password": "mypassword123"
}
```
**Success response (200):**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "tokenType": "bearer",
  "user": {
    "id": "abc-uuid",
    "name": "Raj Kumar",
    "email": "raj@example.com",
    "phone": "9988776655"
  }
}
```

> ⚠️ **Save `accessToken` and `user.id` to SharedPreferences after login.**
> Every subsequent request needs `Authorization: Bearer <accessToken>` header.

**Retrofit interface:**
```kotlin
@POST("api/auth/login")
suspend fun login(@Body request: LoginRequest): Response<LoginResponse>
```

---

## 3. Kitchen Status (Show on Home Screen)

```
GET /api/kitchen/status
Auth: Not required
```
**Response (200):**
```json
{
  "isAcceptingOrders": true,
  "activeOrdersCount": 3,
  "estimatedWaitMinutes": 19,
  "message": "We're open! Estimated wait: 19 minutes."
}
```

**Android usage:**
- Call this on **app launch / home screen load**
- If `isAcceptingOrders = false` → disable "Order" button, show `message` in a banner
- If `isAcceptingOrders = true` → show `"~19 min wait"` badge on home screen

```kotlin
@GET("api/kitchen/status")
suspend fun getKitchenStatus(): Response<KitchenStatusResponse>
```

---

## 4. Menu

### 4a. Get All Categories
```
GET /api/menu/categories
Auth: Not required
```
**Response (200):**
```json
[
  { "id": "uuid", "name": "Pizza",    "iconUrl": "/icons/pizza.png",   "displayOrder": 1, "itemCount": 2 },
  { "id": "uuid", "name": "Burgers",  "iconUrl": "/icons/burger.png",  "displayOrder": 2, "itemCount": 2 },
  { "id": "uuid", "name": "Drinks",   "iconUrl": "/icons/drink.png",   "displayOrder": 3, "itemCount": 1 },
  { "id": "uuid", "name": "Desserts", "iconUrl": "/icons/dessert.png", "displayOrder": 4, "itemCount": 1 }
]
```
**Android usage:** Render as horizontal chip/tab bar at top of menu screen.

---

### 4b. Get Items in a Category
```
GET /api/menu/category/{categoryId}
Auth: Not required
```
**Response (200):** Array of `MenuItemResponse`
```json
[
  {
    "id": "uuid",
    "name": "Margherita Pizza",
    "price": "12.99",
    "originalPrice": "15.99",
    "discountPercent": "18.76",
    "categoryId": "uuid",
    "imageUrl": "/images/pizza.png",
    "specialOffer": true,
    "isAvailable": true,
    "preparationTimeMinutes": 15
  }
]
```
**Android usage:** On category chip tap → call this, show in RecyclerView / LazyColumn.

---

### 4c. Get All Discount Items (Home Screen "Deals" Section)
```
GET /api/menu/discounts
Auth: Not required
```
**Response (200):** Same as above but only items with `discountPercent > 0`

**Android usage:** Show as horizontal "🔥 Today's Deals" scroll on home screen.

---

### 4d. Get All Menu Items
```
GET /api/menu
Auth: Not required
```
Returns all available items (no category filter).

---

### 4e. Search Menu
```
GET /api/menu/search?q=pizza
Auth: Not required
```
**Android usage:** Call on every keypress (debounced 300ms) in search bar.

```kotlin
@GET("api/menu/search")
suspend fun searchMenu(@Query("q") query: String): Response<List<MenuItemResponse>>
```

---

## 5. Cart

> All cart endpoints require `Authorization: Bearer <token>`

### 5a. View Cart
```
GET /api/cart
Auth: Required
```
**Response (200):**
```json
{
  "items": [
    {
      "id": "cart-item-uuid",
      "menuItemId": "menu-uuid",
      "quantity": 1,
      "itemName": "Margherita Pizza",
      "itemPrice": "12.99",
      "itemOriginalPrice": "15.99",
      "itemDiscountPercent": "18.76",
      "itemImageUrl": "/images/pizza.png",
      "itemIsAvailable": true,
      "lineTotal": "12.99"
    }
  ],
  "subtotal": "34.99",
  "totalItems": 5
}
```

---

### 5b. Add Item to Cart
```
POST /api/cart/items
Auth: Required
```
**Request:**
```json
{
  "menuItemId": "menu-uuid",
  "quantity": 1
}
```
**Response (201):** `CartItemResponse` (same as one item in cart)

> If the same item is added again, the quantity is **incremented** (not duplicated).

```kotlin
@POST("api/cart/items")
suspend fun addToCart(@Body request: AddToCartRequest): Response<CartItemResponse>
```

---

### 5c. Update Cart Item Quantity
```
PATCH /api/cart/items/{cartItemId}
Auth: Required
```
**Request:**
```json
{ "quantity": 3 }
```
**Response (200):** Updated `CartItemResponse`

---

### 5d. Remove Item from Cart
```
DELETE /api/cart/items/{cartItemId}
Auth: Required
```
**Response: 204 No Content** (no body)

---

### 5e. Clear Entire Cart
```
DELETE /api/cart
Auth: Required
```
**Response: 204 No Content**

---

### 5f. Validate Cart Before Checkout ⚠️
```
POST /api/cart/validate
Auth: Required
(no body needed — server reads user's cart automatically)
```
**Response (200) — All good:**
```json
{
  "isValid": true,
  "issues": [],
  "currentTotal": "34.99"
}
```
**Response (200) — Problems found:**
```json
{
  "isValid": false,
  "issues": [
    {
      "menuItemId": "uuid",
      "itemName": "Margherita Pizza",
      "issue": "UNAVAILABLE"
    }
  ],
  "currentTotal": "22.00"
}
```
**Android usage:**
- Call this when user taps **"Proceed to Checkout"**
- If `isValid = false` → show an alert: *"Margherita Pizza is no longer available. It was removed."*
- Only proceed to place order if `isValid = true`

---

## 6. ETA Preview (Show on Cart / Checkout Screen)

```
POST /api/kitchen/eta
Auth: Not required
```
**Request:**
```json
{
  "items": [
    { "menuItemId": "uuid1", "quantity": 1 },
    { "menuItemId": "uuid2", "quantity": 2 }
  ]
}
```
**Response (200):**
```json
{
  "estimatedReadyMinutes": 15,
  "estimatedReadyAt": "2026-07-10T03:15:00Z",
  "basePrepMinutes": 15,
  "queueBufferMinutes": 0
}
```
**Android usage:**
- Build the item list from current cart contents
- Show `"Ready in ~15 min"` or `"Ready by 9:15 PM"` on the checkout screen

```kotlin
@POST("api/kitchen/eta")
suspend fun getEtaPreview(@Body request: EtaPreviewRequest): Response<EtaPreviewResponse>
```

---

## 7. Place Order

```
POST /api/orders
Auth: Required
```
**Request:**
```json
{
  "userId": "user-uuid-from-login",
  "totalAmount": 34.99,
  "notes": "Extra ketchup please!",
  "scheduledDate": "2026-07-11",
  "scheduledSlotId": "uuid-of-timeslot"
}
```
> **Note:** Do NOT pass `items` array — server will pull from cart automatically.
> `userId` must match the token's user. `totalAmount` is validated server-side.
> `scheduledDate` and `scheduledSlotId` are optional. If omitted, order is placed for immediate preparation.

**Success response (201):**
```json
{
  "id": "order-uuid",
  "userId": "user-uuid",
  "totalAmount": "34.99",
  "status": "SCHEDULED",
  "pickupNumber": 7,
  "pickupDate": "2026-07-10",
  "estimatedReadyAt": "2026-07-11T09:30:00Z",
  "actualReadyAt": null,
  "notes": "Extra ketchup please!",
  "createdAt": "2026-07-10T03:00:00Z",
  "items": [
    {
      "id": "oi-uuid",
      "orderId": "order-uuid",
      "menuItemId": "menu-uuid",
      "itemName": "Margherita Pizza",
      "quantity": 1,
      "priceAtTimeOfOrder": "12.99",
      "lineTotal": "12.99"
    }
  ],
  "scheduledDate": "2026-07-11",
  "scheduledSlotId": "uuid-of-timeslot",
  "scheduledSlot": {
    "id": "uuid-of-timeslot",
    "startTime": "09:00:00",
    "endTime": "09:30:00",
    "maxOrders": 5,
    "isAvailable": true
  }
}
```

---

### 7b. Get Available Time Slots for Scheduling
```
GET /api/orders/schedule/slots?date=YYYY-MM-DD
Auth: Not required
```
**Response (200):**
```json
[
  {
    "id": "slot-uuid-1",
    "startTime": "09:00:00",
    "endTime": "09:30:00",
    "maxOrders": 5,
    "ordersBooked": 2,
    "ordersRemaining": 3,
    "isAvailable": true
  },
  {
    "id": "slot-uuid-2",
    "startTime": "09:30:00",
    "endTime": "10:00:00",
    "maxOrders": 5,
    "ordersBooked": 5,
    "ordersRemaining": 0,
    "isAvailable": false
  }
]
```
**Android usage:** 
- Fetch this on Checkout screen after date picker selection.
- Render time slots as grid options. Disable slots where `isAvailable = false`.

**What happens after success:**
1. Save `id` (orderId) and `pickupNumber` locally
2. Navigate to **Order Tracking Screen**
3. Display pickup number `#7` prominently
4. Open SSE stream for real-time updates (see Section 8)
5. The cart is now **empty on the server** (auto-cleared)

**Error responses:**
- `400` – Total amount mismatch / item unavailable / cart empty / kitchen closed
- `401` – Token expired → go to login
- `404` – User or menu item not found

```kotlin
@POST("api/orders")
suspend fun placeOrder(@Body request: CreateOrderRequest): Response<OrderResponse>
```

---

## 8. Real-Time Order Tracking via SSE

```
GET /api/orders/stream/{userId}
Auth: Required (token as header)
Accept: text/event-stream
```

> **This is a persistent connection.** The server keeps it open and pushes events as the order status changes.

### How to implement in Android (OkHttp):
```kotlin
class OrderSseClient(private val userId: String, private val token: String) {

    private val client = OkHttpClient.Builder()
        .readTimeout(0, TimeUnit.MILLISECONDS)  // no read timeout for SSE!
        .build()

    fun startListening(onStatus: (OrderStatusEvent) -> Unit, onError: (String) -> Unit) {
        val request = Request.Builder()
            .url("http://192.168.x.x:8000/api/orders/stream/$userId")
            .header("Authorization", "Bearer $token")
            .header("Accept", "text/event-stream")
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                onError("Connection failed: ${e.message}")
            }

            override fun onResponse(call: Call, response: Response) {
                response.body?.source()?.let { source ->
                    var currentEvent = ""
                    while (!source.exhausted()) {
                        val line = source.readUtf8Line() ?: break
                        when {
                            line.startsWith("event:") -> currentEvent = line.removePrefix("event:").trim()
                            line.startsWith("data:") && currentEvent == "order-status" -> {
                                val json = line.removePrefix("data:").trim()
                                val event = Gson().fromJson(json, OrderStatusEvent::class.java)
                                onStatus(event)
                            }
                            line.startsWith("data:") && currentEvent == "connected" -> {
                                // Stream is live
                            }
                        }
                    }
                }
            }
        })
    }

    fun stop() { client.dispatcher.cancelAll() }
}
```

### SSE Event structure received:
```json
{
  "orderId": "order-uuid",
  "userId": "user-uuid",
  "status": "PREPARING",
  "pickupNumber": 7,
  "estimatedReadyAt": "2026-07-10T03:15:00Z",
  "updatedAt": "2026-07-10T03:01:00Z"
}
```

### Status flow:
```
PLACED / SCHEDULED  →  PREPARING  →  READY_FOR_PICKUP  →  DELIVERED
```

| Status | Show to user |
|---|---|
| `PLACED` | "Order placed! Preparing soon..." 🟡 |
| `SCHEDULED` | "Order scheduled! Cooking starts later..." ⏳ |
| `PREPARING` | "Your food is being cooked! 🍳" 🟠 |
| `READY_FOR_PICKUP` | "Ready! Show **#7** at the counter ✅" 🟢 |
| `DELIVERED` | "Order complete. Thank you! 🙌" ⚫ |

> Open the SSE stream right after `POST /orders` succeeds.
> Close it (`.stop()`) when user navigates away from the tracking screen.

---

## 9. Order History

```
GET /api/orders/history?page=1&limit=10
Auth: Required
```
**Response (200):**
```json
{
  "orders": [
    {
      "id": "order-uuid",
      "totalAmount": "34.99",
      "status": "DELIVERED",
      "pickupNumber": 7,
      "pickupDate": "2026-07-10",
      "estimatedReadyAt": "2026-07-10T03:15:00Z",
      "actualReadyAt": "2026-07-10T03:10:00Z",
      "notes": "Extra ketchup please!",
      "createdAt": "2026-07-10T03:00:00Z",
      "items": [ ... ]
    }
  ],
  "total": 12,
  "page": 1,
  "limit": 10
}
```
**Android usage:** Infinite scroll — increment `page` as user scrolls down.

```kotlin
@GET("api/orders/history")
suspend fun getOrderHistory(
    @Query("page") page: Int = 1,
    @Query("limit") limit: Int = 10
): Response<OrderHistoryResponse>
```

---

## 10. Single Order Detail

```
GET /api/orders/{orderId}
Auth: Required
```
Returns a single `OrderResponse`. Use for order detail screen.

---

## 11. Help / FAQ

### 11a. Get All FAQ
```
GET /api/help/faq
Auth: Not required
```
**Response (200):**
```json
[
  {
    "id": "uuid",
    "title": "Ordering",
    "icon": "🛒",
    "displayOrder": 1,
    "items": [
      {
        "id": "uuid",
        "question": "How do I place an order?",
        "answer": "Browse the menu, add items to cart..."
      }
    ]
  }
]
```
**Android usage:** Accordion/expand UI per category.

---

### 11b. Submit Support Ticket
```
POST /api/help/tickets
Auth: Required
```
**Request:**
```json
{
  "subject": "My order is taking too long",
  "message": "It has been 30 minutes and my order is still pending."
}
```
**Response (201):**
```json
{
  "id": "ticket-uuid",
  "subject": "My order is taking too long",
  "message": "...",
  "status": "OPEN",
  "createdAt": "2026-07-10T03:00:00Z"
}
```

---

### 11c. View My Tickets
```
GET /api/help/tickets
Auth: Required
```
Returns list of `TicketResponse`.

---

## 12. Error Handling

All errors follow this format:
```json
{
  "timestamp": "2026-07-10T03:00:00Z",
  "status": 400,
  "error": "Bad Request",
  "message": "Order total does not match menu prices. Expected: 34.99, received: 30.00",
  "path": "/api/orders"
}
```

| HTTP Code | Meaning | Android action |
|---|---|---|
| `400` | Bad request / validation failed | Show `message` to user in a Snackbar/Dialog |
| `401` | Unauthorized / token expired | Clear token → navigate to Login screen |
| `404` | Resource not found | Show "Not found" error |
| `500` | Server error | Show "Something went wrong. Try again." |

**Retrofit global error handler:**
```kotlin
suspend fun <T> safeApiCall(call: suspend () -> Response<T>): Result<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            Result.success(response.body()!!)
        } else {
            val error = Gson().fromJson(response.errorBody()?.string(), ApiError::class.java)
            Result.failure(Exception(error.message))
        }
    } catch (e: Exception) {
        Result.failure(e)
    }
}
```

---

## 13. Data Models (Kotlin)

```kotlin
// Auth
data class RegisterRequest(val name: String, val email: String, val password: String, val phone: String?)
data class LoginRequest(val email: String, val password: String)
data class LoginResponse(val accessToken: String, val tokenType: String, val user: UserResponse)
data class UserResponse(val id: String, val name: String, val email: String, val phone: String?)

// Menu
data class CategoryResponse(val id: String, val name: String, val iconUrl: String?, val displayOrder: Int, val itemCount: Int)
data class MenuItemResponse(
    val id: String, val name: String, val price: String, val originalPrice: String?,
    val discountPercent: String?, val categoryId: String?, val imageUrl: String?,
    val specialOffer: Boolean, val isAvailable: Boolean, val preparationTimeMinutes: Int
)

// Cart
data class AddToCartRequest(val menuItemId: String, val quantity: Int)
data class UpdateCartItemRequest(val quantity: Int)
data class CartItemResponse(
    val id: String, val menuItemId: String, val quantity: Int,
    val itemName: String, val itemPrice: String, val itemOriginalPrice: String?,
    val itemDiscountPercent: String?, val itemImageUrl: String?,
    val itemIsAvailable: Boolean, val lineTotal: String
)
data class CartResponse(val items: List<CartItemResponse>, val subtotal: String, val totalItems: Int)
data class CartValidateIssue(val menuItemId: String, val itemName: String, val issue: String)
data class CartValidateResponse(val isValid: Boolean, val issues: List<CartValidateIssue>, val currentTotal: String)

// Kitchen
data class KitchenStatusResponse(val isAcceptingOrders: Boolean, val activeOrdersCount: Int, val estimatedWaitMinutes: Int, val message: String)
data class EtaItem(val menuItemId: String, val quantity: Int)
data class EtaPreviewRequest(val items: List<EtaItem>)
data class EtaPreviewResponse(val estimatedReadyMinutes: Int, val estimatedReadyAt: String, val basePrepMinutes: Int, val queueBufferMinutes: Int)

// Order
data class TimeSlotResponse(
    val id: String,
    val startTime: String,
    val endTime: String,
    val maxOrders: Int,
    val ordersBooked: Int?,
    val ordersRemaining: Int?,
    val isAvailable: Boolean
)

data class CreateOrderRequest(
    val userId: String,
    val totalAmount: Double,
    val notes: String?,
    val scheduledDate: String? = null,
    val scheduledSlotId: String? = null
)

data class OrderItemResponse(val id: String, val orderId: String, val menuItemId: String, val itemName: String, val quantity: Int, val priceAtTimeOfOrder: String, val lineTotal: String)

data class OrderResponse(
    val id: String,
    val userId: String,
    val totalAmount: String,
    val status: String,
    val pickupNumber: Int?,
    val pickupDate: String?,
    val estimatedReadyAt: String?,
    val actualReadyAt: String?,
    val notes: String?,
    val createdAt: String,
    val items: List<OrderItemResponse>,
    val scheduledDate: String? = null,
    val scheduledSlotId: String? = null,
    val scheduledSlot: TimeSlotResponse? = null
)
data class OrderHistoryResponse(val orders: List<OrderResponse>, val total: Int, val page: Int, val limit: Int)

// SSE Event
data class OrderStatusEvent(val orderId: String, val userId: String, val status: String, val pickupNumber: Int?, val estimatedReadyAt: String?, val updatedAt: String)

// Help
data class FaqItemResponse(val id: String, val question: String, val answer: String)
data class FaqCategoryResponse(val id: String, val title: String, val icon: String?, val displayOrder: Int, val items: List<FaqItemResponse>)
data class CreateTicketRequest(val subject: String, val message: String)
data class TicketResponse(val id: String, val subject: String, val message: String, val status: String, val createdAt: String)

// Error
data class ApiError(val timestamp: String, val status: Int, val error: String, val message: String, val path: String)
```

---

## 14. Screen → API Call Map

| Android Screen | API calls to make |
|---|---|
| **Splash** | `GET /kitchen/status` |
| **Register** | `POST /auth/register` |
| **Login** | `POST /auth/login` → save token + userId |
| **Home** | `GET /kitchen/status`, `GET /menu/discounts`, `GET /menu/categories` |
| **Menu** | `GET /menu/categories`, `GET /menu/category/{id}` on chip tap |
| **Search** | `GET /menu/search?q=...` (debounced) |
| **Cart** | `GET /cart`, `POST /cart/validate`, `POST /kitchen/eta` |
| **Add to cart button** | `POST /cart/items` |
| **Checkout confirm** | `POST /orders`, `GET /orders/schedule/slots?date=...` (optional scheduling) |
| **Order Tracking** | Open `GET /orders/stream/{userId}` SSE stream |
| **Order History** | `GET /orders/history?page=1` |
| **Order Detail** | `GET /orders/{id}` |
| **Help / FAQ** | `GET /help/faq` |
| **Contact Support** | `POST /help/tickets`, `GET /help/tickets` |

---

## 15. Quick Notes for Android Dev

1. **Token storage:** Use `EncryptedSharedPreferences` to store the `accessToken` securely.
2. **Token expiry:** If any request returns `401`, clear stored token and redirect to Login.
3. **SSE timeout:** Set OkHttp `readTimeout(0, MILLISECONDS)` — SSE connections must not timeout.
4. **Close SSE:** Always cancel the SSE call in `onPause()` or `onDestroyView()` to avoid leaks.
5. **Prices are Strings:** Server returns prices as `"12.99"` (String) for precision. Parse with `BigDecimal("12.99")` in Android, never `Double`.
6. **Cart total math:** Do NOT calculate cart total on the client. Use `subtotal` from `GET /cart` and `currentTotal` from `POST /cart/validate`.
7. **Place order total:** Pass the `currentTotal` from the validate response as `totalAmount` in `POST /orders`. Server validates it against DB prices.
8. **Pagination:** `GET /orders/history` is paginated. Start at `page=1`, `limit=10`. Load more on scroll.
9. **Image URLs:** Prefix with your base URL: `http://192.168.x.x:8000` + `imageUrl`.
10. **Offline mode:** Cache `GET /menu/categories` and `GET /menu` locally (Room DB) for offline browsing. Cart and orders always require network.
