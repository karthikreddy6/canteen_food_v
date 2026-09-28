import pytest
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import User, College, Canteen, MenuItem, college_canteens
from app.security import create_access_token, hash_password


@pytest.mark.asyncio(loop_scope="module")
async def test_user_can_only_see_their_college_menu_items(async_client):
    """
    Verify that an authenticated user can ONLY see menu items from their own college canteens.
    Engineering College has Central Canteen and Hostel Canteen.
    Science College has Science Canteen.
    Arts College has Arts Canteen.
    """
    async with AsyncSessionLocal() as db:
        # Load colleges
        eng_col = (await db.execute(select(College).where(College.name == "Engineering College"))).scalar_one()
        science_col = (await db.execute(select(College).where(College.name == "Science College"))).scalar_one()
        arts_col = (await db.execute(select(College).where(College.name == "Arts College"))).scalar_one()

        # Load canteens
        central_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Central Canteen"))).scalar_one()
        hostel_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Hostel Canteen"))).scalar_one()
        science_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Science Canteen"))).scalar_one()
        arts_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Arts Canteen"))).scalar_one()

        # Create or fetch an Engineering student
        eng_user = (await db.execute(select(User).where(User.email == "eng_student@test.com"))).scalars().first()
        if not eng_user:
            eng_user = User(
                id="eng-student-uuid-001",
                name="Eng Student",
                email="eng_student@test.com",
                phone="919999000001",
                phone_verified=True,
                college="Engineering College",
                college_id=eng_col.id,
                preferred_canteen_id=central_canteen.id,
                hashed_password=hash_password("password123"),
            )
            db.add(eng_user)

        # Create or fetch an Arts student
        arts_user = (await db.execute(select(User).where(User.email == "arts_student@test.com"))).scalars().first()
        if not arts_user:
            arts_user = User(
                id="arts-student-uuid-002",
                name="Arts Student",
                email="arts_student@test.com",
                phone="919999000002",
                phone_verified=True,
                college="Arts College",
                college_id=arts_col.id,
                preferred_canteen_id=arts_canteen.id,
                hashed_password=hash_password("password123"),
            )
            db.add(arts_user)

        await db.commit()

    eng_token = create_access_token(eng_user.id)
    eng_headers = {
        "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
        "Authorization": f"Bearer {eng_token}",
    }

    arts_token = create_access_token(arts_user.id)
    arts_headers = {
        "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
        "Authorization": f"Bearer {arts_token}",
    }

    # 1. Engineering student GET /api/menu -> should only contain Engineering College items
    res = await async_client.get("/api/menu", headers=eng_headers)
    assert res.status_code == 200
    items = res.json()
    assert len(items) > 0
    for item in items:
        # Item canteen must be Central Canteen or Hostel Canteen
        assert item["canteenId"] in [str(central_canteen.id), str(hostel_canteen.id)]
        assert item["canteenId"] != str(science_canteen.id)
        assert item["canteenId"] != str(arts_canteen.id)

    # 2. Engineering student explicitly querying Hostel Canteen (in their college) -> SUCCESS
    res_hostel = await async_client.get(f"/api/menu?canteenId={hostel_canteen.id}", headers=eng_headers)
    assert res_hostel.status_code == 200
    hostel_items = res_hostel.json()
    assert len(hostel_items) > 0
    for item in hostel_items:
        assert item["canteenId"] == str(hostel_canteen.id)

    # 3. Engineering student querying Science Canteen (OUTSIDE their college) -> REJECTED (400)
    res_science = await async_client.get(f"/api/menu?canteenId={science_canteen.id}", headers=eng_headers)
    assert res_science.status_code == 400
    assert "college" in res_science.json().get("message", "").lower()

    # 4. Engineering student querying Arts Canteen (OUTSIDE their college) -> REJECTED (400)
    res_arts = await async_client.get(f"/api/menu?canteenId={arts_canteen.id}", headers=eng_headers)
    assert res_arts.status_code == 400
    assert "college" in res_arts.json().get("message", "").lower()

    # 5. Arts student GET /api/menu -> should only contain Arts College items
    res_arts_menu = await async_client.get("/api/menu", headers=arts_headers)
    assert res_arts_menu.status_code == 200
    arts_items = res_arts_menu.json()
    assert len(arts_items) > 0
    for item in arts_items:
        assert item["canteenId"] == str(arts_canteen.id)
        assert item["canteenId"] not in [str(central_canteen.id), str(hostel_canteen.id), str(science_canteen.id)]

    # 6. Arts student trying to query Central Canteen (OUTSIDE Arts college) -> REJECTED (400)
    res_arts_block = await async_client.get(f"/api/menu?canteenId={central_canteen.id}", headers=arts_headers)
    assert res_arts_block.status_code == 400


@pytest.mark.asyncio(loop_scope="module")
async def test_search_and_specials_scoped_to_college(async_client):
    """Verify search, specials, discounts, and categories are strictly scoped to the student's college."""
    async with AsyncSessionLocal() as db:
        eng_col = (await db.execute(select(College).where(College.name == "Engineering College"))).scalar_one()
        central_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Central Canteen"))).scalar_one()

        eng_user = (await db.execute(select(User).where(User.email == "eng_student@test.com"))).scalar_one()

    eng_token = create_access_token(eng_user.id)
    eng_headers = {
        "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
        "Authorization": f"Bearer {eng_token}",
    }

    # "Chilli Chicken" is in Science Canteen (special_offer=True)
    # Engineering student search for "Chilli" must return 0 items
    search_res = await async_client.get("/api/menu/search?q=Chilli", headers=eng_headers)
    assert search_res.status_code == 200
    search_items = search_res.json()
    assert len(search_items) == 0

    # Engineering student search for "Biryani" returns Chicken Biryani (Central Canteen)
    search_biryani = await async_client.get("/api/menu/search?q=Biryani", headers=eng_headers)
    assert search_biryani.status_code == 200
    biryani_items = search_biryani.json()
    assert len(biryani_items) > 0
    assert all("biryani" in item["name"].lower() for item in biryani_items)

    # Engineering specials should NOT include Chocolate Brownie (Arts) or Chilli Chicken (Science)
    specials_res = await async_client.get("/api/menu/specials", headers=eng_headers)
    assert specials_res.status_code == 200
    specials = specials_res.json()
    for item in specials:
        assert item["name"] not in ["Chocolate Brownie", "Chilli Chicken"]

    # Discounts should only be from Engineering College
    discounts_res = await async_client.get("/api/menu/discounts", headers=eng_headers)
    assert discounts_res.status_code == 200
    discounts = discounts_res.json()
    for item in discounts:
        assert item["name"] != "Chocolate Brownie"


@pytest.mark.asyncio(loop_scope="module")
async def test_cart_and_order_prevent_other_college_items(async_client):
    """Verify that adding an item from another college's canteen to cart is rejected."""
    async with AsyncSessionLocal() as db:
        science_canteen = (await db.execute(select(Canteen).where(Canteen.name == "Science Canteen"))).scalar_one()
        science_item = (await db.execute(select(MenuItem).where(MenuItem.canteen_id == science_canteen.id))).scalars().first()
        eng_user = (await db.execute(select(User).where(User.email == "eng_student@test.com"))).scalar_one()

    eng_token = create_access_token(eng_user.id)
    eng_headers = {
        "X-App-Key": "ONFOOD_SECURE_CLIENT_APP_KEY_2026",
        "Authorization": f"Bearer {eng_token}",
    }

    # Clear cart first
    await async_client.delete("/api/cart", headers=eng_headers)

    # Attempt to add Science Canteen item to Engineering student's cart -> 400 Bad Request
    cart_res = await async_client.post("/api/cart/items", headers=eng_headers, json={
        "menuItemId": str(science_item.id),
        "quantity": 1,
    })
    assert cart_res.status_code == 400
    assert "college" in cart_res.json().get("message", "").lower()
