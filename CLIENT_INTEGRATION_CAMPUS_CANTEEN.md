# Customer App Integration

After login, store `collegeId` and `preferredCanteenId` from the user response.

On registration, show college first, and then only the canteens linked to that college. If there is one canteen, select it automatically; otherwise show a canteen picker.

Pass the selected canteen ID to menu, search, specials, discounts, and category requests using the `canteenId` query parameter. Keep the selected canteen in the app session and show its name above the menu.

When adding to cart, reject a second canteen locally and display: `Your cart can contain items from only one canteen.` The server also enforces this rule.

Load advertisements after authentication from `GET /api/banners`; the server filters them for the student's college and preferred canteen.
