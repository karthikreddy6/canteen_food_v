# College and Canteen Changes

The customer API now supports college onboarding, canteen-specific menus, and targeted banners.

## Registration flow

1. `GET /api/locations/colleges`
2. `GET /api/locations/colleges/{collegeId}/canteens`
3. Send `collegeId` and `preferredCanteenId` to `POST /api/auth/register`.

The `college` text field remains for compatibility, but new clients should use IDs.

## Menu and cart

Use `GET /api/menu?canteenId={canteenId}`. A cart may contain items from only one canteen, and an order stores its `canteenId`.

## Banners

`GET /api/banners` returns global, college-matching, and preferred-canteen-matching banners for the authenticated student.

## Demo data

- Engineering College and Business College share Central Canteen and Hostel Canteen.
- Arts College uses Arts Canteen.
- Science College uses Science Canteen.
- Vendor logins: `central@onfood.local`, `hostel@onfood.local`, `arts@onfood.local`, `science@onfood.local`.
- Demo vendor password: `vendor_password`.
