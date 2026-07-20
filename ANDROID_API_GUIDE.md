# OnFood Android <-> Server API Integration Guide
### Last Updated: July 19, 2026

## Base Configuration

```text
Base URL      : http://<your-server-ip>:8000
Content-Type  : application/json
Auth Header   : Authorization: Bearer <access_token>
Response Type : JSON (camelCase fields)
```

All request bodies are JSON. All responses are JSON with camelCase keys.

## Core Rules

1. Every student belongs to one college and one preferred canteen.
2. Menu items belong to a canteen. Pass `?canteenId=<uuid>` to menu endpoints.
3. Cart is single-canteen. The server enforces this.
4. `GET /api/banners` is personalized using the logged-in student's `collegeId` and `preferredCanteenId`.
5. Show `order.orderToken` as the receipt number.

## Registration Flow

```text
Step 1 -> Basic info
Step 2 -> Pick College       -> GET /api/locations/colleges
          Not listed?        -> POST /api/locations/colleges/suggest
Step 3 -> Pick Canteen       -> GET /api/locations/colleges/{collegeId}/canteens
Final  -> Register           -> POST /api/auth/register
Then   -> Verify OTP         -> POST /api/auth/verify-otp
```

### List Colleges

```http
GET /api/locations/colleges
```

Response:

```json
[
  { "id": "college-uuid", "name": "Engineering College", "isActive": true }
]
```

### Suggest College

```http
POST /api/locations/colleges/suggest
```

Request:

```json
{ "name": "New Engineering College" }
```

Response:

```json
{
  "id": "new-college-uuid",
  "name": "New Engineering College",
  "isActive": false,
  "suggested": true,
  "pendingApproval": true,
  "message": "'New Engineering College' has been submitted for approval. You can continue registration using this college."
}
```

The suggested college is stored as a requested college and can be used immediately in registration.

### List Canteens for a College

```http
GET /api/locations/colleges/{collegeId}/canteens
```

Response:

```json
[
  { "id": "canteen-uuid", "name": "Central Canteen", "isActive": true }
]
```

If only one canteen is returned, auto-select it.

### Register

```http
POST /api/auth/register
```

Request:

```json
{
  "name": "Raj Kumar",
  "email": "raj@example.com",
  "password": "mypassword123",
  "phone": "91998776655",
  "rollNumber": "22CS101",
  "college": "Engineering College",
  "collegeId": "college-uuid",
  "preferredCanteenId": "canteen-uuid"
}
```

Notes:
- `phone`, `collegeId`, and `preferredCanteenId` are required.
- The server validates the selected college/canteen combination.
- Success returns `RegistrationOtpResponse`.
- The account stays pending until OTP verification succeeds.

### Verify OTP

```http
POST /api/auth/verify-otp
```

Request:

```json
{
  "email": "raj@example.com",
  "otp": "123456"
}
```

Response:

```json
{
  "accessToken": "eyJ...",
  "tokenType": "bearer",
  "user": {
    "id": "user-uuid",
    "name": "Raj Kumar",
    "email": "raj@example.com",
    "rollNumber": "22CS101",
    "college": "Engineering College",
    "collegeId": "college-uuid",
    "preferredCanteenId": "canteen-uuid",
    "phoneVerified": true,
    "useRollNumberAsOrderToken": false
  }
}
```

### Resend OTP

```http
POST /api/auth/resend-otp
```

Request:

```json
{
  "email": "raj@example.com",
  "password": "mypassword123"
}
```

Response:

```json
{
  "verificationRequired": true,
  "expiresInMinutes": 5,
  "message": "A new verification code was sent to your WhatsApp number."
}
```

### Login

```http
POST /api/auth/login
```

Request:

```json
{ "email": "raj@example.com", "password": "mypassword123" }
```

Response:

```json
{
  "accessToken": "eyJ...",
  "tokenType": "bearer",
  "user": {
    "id": "user-uuid",
    "name": "Raj Kumar",
    "email": "raj@example.com",
    "rollNumber": "22CS101",
    "college": "Engineering College",
    "collegeId": "college-uuid",
    "preferredCanteenId": "canteen-uuid",
    "phoneVerified": true,
    "useRollNumberAsOrderToken": false
  }
}
```

Save:
- `accessToken`
- `user.id`
- `user.collegeId`
- `user.preferredCanteenId`
- `user.rollNumber`
- `user.phoneVerified`

### Update Profile

```http
PATCH /api/auth/profile
```

Request fields are optional:

```json
{
  "name": "Raj Kumar",
  "phone": "9988776655",
  "password": "newpassword",
  "rollNumber": "22CS101",
  "college": "Engineering College",
  "collegeId": "college-uuid",
  "preferredCanteenId": "canteen-uuid",
  "useRollNumberAsOrderToken": true
}
```

## Kitchen

### Kitchen Status

```http
GET /api/kitchen/status
```

### ETA Preview

```http
POST /api/kitchen/eta
```

Request:

```json
{
  "items": [
    { "menuItemId": "uuid", "quantity": 1 }
  ]
}
```

## Menu

Always pass `?canteenId=<user.preferredCanteenId>` where relevant.

### Sync

```http
GET /api/menu/sync
GET /api/menu/sync?since=2026-07-10T10:00:00
```

Example:

```json
{
  "categories": [
    {
      "id": "uuid",
      "name": "Biryani",
      "iconUrl": "/icons/biryani.png",
      "displayOrder": 1,
      "itemCount": 2,
      "updatedAt": "2026-07-17T08:00:00"
    }
  ],
  "items": [
    {
      "id": "uuid",
      "name": "Chicken Biryani",
      "price": "160.00",
      "originalPrice": "190.00",
      "discountPercent": "15.79",
      "categoryId": "uuid",
      "canteenId": "canteen-uuid",
      "imageUrl": "/images/chicken-biryani.png",
      "specialOffer": true,
      "isAvailable": true,
      "preparationTimeMinutes": 18,
      "updatedAt": "2026-07-17T08:00:00"
    }
  ],
  "serverTime": "2026-07-17T08:00:00"
}
```

### Categories

```http
GET /api/menu/categories
```

### All Menu Items

```http
GET /api/menu?canteenId=<uuid>
```

### Paged Menu

```http
GET /api/menu/paged?page=1&limit=20&categoryId=<uuid>&canteenId=<uuid>
```

### Discounts

```http
GET /api/menu/discounts?canteenId=<uuid>
```

### Specials

```http
GET /api/menu/specials?canteenId=<uuid>
```

### Search

```http
GET /api/menu/search?q=biryani&canteenId=<uuid>
```

### By Category

```http
GET /api/menu/category/{categoryId}?canteenId=<uuid>
```

## Promotions

### Banners

```http
GET /api/banners
```

Auth required.

### Coupon Validation

```http
GET /api/coupons/{code}
```

### Apply Coupon Preview

```http
POST /api/coupons/apply
```

Send the coupon code with cart item IDs and quantities. The server loads
current menu prices and returns the item prices, subtotal, discount, and final
display total. This preview does not create an order or consume coupon usage.

Request:

```json
{
  "couponCode": "SAVE10",
  "items": [{ "menuItemId": "uuid", "quantity": 2 }]
}
```

Response:

```json
{
  "couponCode": "SAVE10",
  "isValid": true,
  "items": [{ "menuItemId": "uuid", "quantity": 2, "itemPrice": "160.00", "lineTotal": "320.00" }],
  "subtotal": "320.00",
  "discountAmount": "32.00",
  "totalAmount": "288.00",
  "message": "Coupon applied successfully"
}
```

## Cart

All cart endpoints require auth.

### Get Cart

```http
GET /api/cart
```

### Add Item

```http
POST /api/cart/items
```

Request:

```json
{ "menuItemId": "uuid", "quantity": 1 }
```

Response type: `CartItemResponse`

### Update Item Quantity

```http
PATCH /api/cart/items/{cartItemId}
```

Request:

```json
{ "quantity": 3 }
```

Response type: `CartItemResponse`

### Remove Item

```http
DELETE /api/cart/items/{cartItemId}
```

### Clear Cart

```http
DELETE /api/cart
```

### Validate Cart

```http
POST /api/cart/validate
```

This endpoint:
- checks unavailable items
- returns server-calculated `currentTotal`

Example failure:

```json
{
  "isValid": false,
  "issues": [
    { "menuItemId": "uuid", "itemName": "Chicken Biryani", "issue": "UNAVAILABLE" }
  ],
  "currentTotal": "22.00"
}
```

## Orders

### Place Order

```http
POST /api/orders
```

Immediate order:

```json
{
  "userId": "user-uuid",
  "totalAmount": "34.99",
  "notes": "Extra ketchup please!",
  "couponCode": "SAVE10"
}
```

Scheduled order:

```json
{
  "userId": "user-uuid",
  "totalAmount": "12.99",
  "scheduledDate": "2026-07-18",
  "scheduledSlotId": "slot-uuid"
}
```

### Schedule Slots

```http
GET /api/orders/schedule/slots?date=2026-07-18
```

### Order History

```http
GET /api/orders/history?page=1&limit=10
```

### Order Detail

```http
GET /api/orders/{orderId}
```

### SSE Stream

```http
GET /api/orders/stream/{userId}
Accept: text/event-stream
```

Auth required.

## Help / FAQ

```http
GET /api/help/faq
POST /api/help/tickets
GET /api/help/tickets
```

## Kotlin Models

```kotlin
data class LocationItem(val id: String, val name: String, val isActive: Boolean)
data class SuggestCollegeRequest(val name: String)
data class SuggestCollegeResponse(
    val id: String,
    val name: String,
    val isActive: Boolean,
    val suggested: Boolean,
    val pendingApproval: Boolean,
    val message: String
)

data class RegisterRequest(
    val name: String,
    val email: String,
    val password: String,
    val phone: String,
    val rollNumber: String,
    val college: String,
    val collegeId: String,
    val preferredCanteenId: String
)

data class LoginRequest(val email: String, val password: String)
data class LoginResponse(val accessToken: String, val tokenType: String, val user: UserResponse)
data class UserResponse(
    val id: String,
    val name: String,
    val email: String,
    val phone: String? = null,
    val rollNumber: String? = null,
    val college: String? = null,
    val collegeId: String? = null,
    val preferredCanteenId: String? = null,
    val phoneVerified: Boolean = false,
    val useRollNumberAsOrderToken: Boolean = false
)

data class RegistrationOtpResponse(
    val verificationRequired: Boolean = true,
    val expiresInMinutes: Int,
    val message: String
)

data class VerifyRegistrationOtpRequest(val email: String, val otp: String)

data class ResendRegistrationOtpRequest(val email: String, val password: String)

data class UpdateProfileRequest(
    val name: String? = null,
    val phone: String? = null,
    val password: String? = null,
    val rollNumber: String? = null,
    val college: String? = null,
    val collegeId: String? = null,
    val preferredCanteenId: String? = null,
    val useRollNumberAsOrderToken: Boolean? = null
)

data class AddToCartRequest(val menuItemId: String, val quantity: Int)
data class UpdateCartItemRequest(val quantity: Int)
data class CartItemResponse(
    val id: String,
    val menuItemId: String,
    val canteenId: String?,
    val quantity: Int,
    val itemName: String,
    val itemPrice: String,
    val itemOriginalPrice: String?,
    val itemDiscountPercent: String?,
    val itemImageUrl: String?,
    val itemIsAvailable: Boolean,
    val lineTotal: String
)

data class CreateOrderRequest(
    val userId: String,
    val totalAmount: String,
    val notes: String? = null,
    val couponCode: String? = null,
    val scheduledDate: String? = null,
    val scheduledSlotId: String? = null
)
```

## Retrofit Interface

```kotlin
interface OnFoodApi {
    @POST("api/auth/register")
    suspend fun register(@Body req: RegisterRequest): Response<RegistrationOtpResponse>

    @POST("api/auth/verify-otp")
    suspend fun verifyOtp(@Body req: VerifyRegistrationOtpRequest): Response<LoginResponse>

    @POST("api/auth/resend-otp")
    suspend fun resendOtp(@Body req: ResendRegistrationOtpRequest): Response<RegistrationOtpResponse>

    @POST("api/auth/login")
    suspend fun login(@Body req: LoginRequest): Response<LoginResponse>

    @PATCH("api/auth/profile")
    suspend fun updateProfile(@Body req: UpdateProfileRequest): Response<UserResponse>

    @GET("api/locations/colleges")
    suspend fun getColleges(): Response<List<LocationItem>>

    @GET("api/locations/colleges/{collegeId}/canteens")
    suspend fun getCanteens(@Path("collegeId") collegeId: String): Response<List<LocationItem>>

    @POST("api/locations/colleges/suggest")
    suspend fun suggestCollege(@Body req: SuggestCollegeRequest): Response<SuggestCollegeResponse>

    @GET("api/kitchen/status")
    suspend fun getKitchenStatus(): Response<KitchenStatusResponse>

    @POST("api/kitchen/eta")
    suspend fun getEta(@Body req: EtaPreviewRequest): Response<EtaPreviewResponse>

    @GET("api/menu/sync")
    suspend fun syncMenu(@Query("since") since: String? = null): Response<MenuSyncResponse>

    @GET("api/menu")
    suspend fun getMenu(@Query("canteenId") canteenId: String? = null): Response<List<MenuItemResponse>>

    @GET("api/menu/paged")
    suspend fun getMenuPaged(
        @Query("page") page: Int,
        @Query("limit") limit: Int,
        @Query("categoryId") categoryId: String? = null,
        @Query("canteenId") canteenId: String? = null
    ): Response<MenuPageResponse>

    @GET("api/menu/categories")
    suspend fun getCategories(): Response<List<CategoryResponse>>

    @GET("api/menu/discounts")
    suspend fun getDiscounts(@Query("canteenId") canteenId: String? = null): Response<List<MenuItemResponse>>

    @GET("api/menu/specials")
    suspend fun getSpecials(@Query("canteenId") canteenId: String? = null): Response<List<MenuItemResponse>>

    @GET("api/menu/search")
    suspend fun searchMenu(@Query("q") q: String, @Query("canteenId") canteenId: String? = null): Response<List<MenuItemResponse>>

    @GET("api/menu/category/{categoryId}")
    suspend fun getByCategory(@Path("categoryId") categoryId: String, @Query("canteenId") canteenId: String? = null): Response<List<MenuItemResponse>>

    @GET("api/banners")
    suspend fun getBanners(): Response<List<BannerResponse>>

    @GET("api/coupons/{code}")
    suspend fun validateCoupon(@Path("code") code: String): Response<CouponResponse>

    @GET("api/cart")
    suspend fun getCart(): Response<CartResponse>

    @POST("api/cart/items")
    suspend fun addToCart(@Body req: AddToCartRequest): Response<CartItemResponse>

    @PATCH("api/cart/items/{id}")
    suspend fun updateCartItem(@Path("id") id: String, @Body req: UpdateCartItemRequest): Response<CartItemResponse>

    @DELETE("api/cart/items/{id}")
    suspend fun removeCartItem(@Path("id") id: String): Response<Unit>

    @DELETE("api/cart")
    suspend fun clearCart(): Response<Unit>

    @POST("api/cart/validate")
    suspend fun validateCart(): Response<CartValidateResponse>

    @POST("api/orders")
    suspend fun createOrder(@Body req: CreateOrderRequest): Response<OrderResponse>

    @GET("api/orders/history")
    suspend fun getOrderHistory(@Query("page") page: Int = 1, @Query("limit") limit: Int = 10): Response<OrderHistoryResponse>

    @GET("api/orders/{id}")
    suspend fun getOrder(@Path("id") id: String): Response<OrderResponse>

    @GET("api/orders/schedule/slots")
    suspend fun getTimeSlots(@Query("date") date: String): Response<List<TimeSlotResponse>>

    @GET("api/help/faq")
    suspend fun getFaq(): Response<List<FaqCategoryResponse>>

    @POST("api/help/tickets")
    suspend fun createTicket(@Body req: CreateTicketRequest): Response<TicketResponse>

    @GET("api/help/tickets")
    suspend fun getTickets(): Response<List<TicketResponse>>
}
```

## Current Seeded Demo Data

| College | Canteen | Vendor Login |
|---|---|---|
| Engineering College | Central Canteen | `central@onfood.local` / `vendor_password` |
| Engineering College | Hostel Canteen | `hostel@onfood.local` / `vendor_password` |
| Business College | MBA Canteen | `mba@onfood.local` / `vendor_password` |
| Business College | Food Court Express | `express@onfood.local` / `vendor_password` |
| Arts College | Arts Canteen | `arts@onfood.local` / `vendor_password` |
| Science College | Science Canteen | `science@onfood.local` / `vendor_password` |

## Client Notes

1. Use `EncryptedSharedPreferences` for token storage.
2. Any `401` should log the user out.
3. For SSE, use `readTimeout(0, MILLISECONDS)`.
4. Prices and totals should be handled as strings / `BigDecimal`, not `Double`.
5. Use `POST /api/cart/validate` before checkout and send that `currentTotal` as `totalAmount`.
6. Prefix `imageUrl` with the base URL before loading images.
