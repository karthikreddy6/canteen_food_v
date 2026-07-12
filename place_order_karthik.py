import asyncio
import json
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app

def p(title, data):
    border = "=" * (len(title) + 4)
    print(f"\n{border}")
    print(f"|  {title}  |")
    print(f"{border}")
    print(json.dumps(data, indent=2, default=str))

async def main():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        # 1. Login
        print("Logging in as karthik@example.com...")
        login_res = await c.post("/api/auth/login", json={
            "email": "karthik@example.com",
            "password": "karthik_password"
        })
        if login_res.status_code != 200:
            print(f"Login failed: {login_res.text}")
            return
            
        login_data = login_res.json()
        token = login_data["accessToken"]
        user_id = login_data["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Logged in successfully. User ID: {user_id}")

        # 2. Get Menu Items to find Margherita Pizza and Double Cheeseburger
        print("\nFetching menu items...")
        menu_res = await c.get("/api/menu")
        menu_items = menu_res.json()
        
        pizza = next((i for i in menu_items if "Margherita Pizza" in i["name"]), None)
        burger = next((i for i in menu_items if "Double Cheeseburger" in i["name"]), None)
        
        if not pizza or not burger:
            print("Failed to find Pizza or Burger in menu.")
            return

        # 3. Add to Cart
        print(f"\nAdding {pizza['name']} (x1) to cart...")
        r1 = await c.post("/api/cart/items", headers=headers, json={
            "menuItemId": pizza["id"],
            "quantity": 1
        })
        print(f"Status: {r1.status_code}")
        
        print(f"Adding {burger['name']} (x2) to cart...")
        r2 = await c.post("/api/cart/items", headers=headers, json={
            "menuItemId": burger["id"],
            "quantity": 2
        })
        print(f"Status: {r2.status_code}")

        # 4. View Cart
        print("\nViewing Cart...")
        cart_res = await c.get("/api/cart", headers=headers)
        p("Current Cart", cart_res.json())
        cart_data = cart_res.json()

        # 5. Place Order
        print("\nPlacing Order...")
        order_res = await c.post("/api/orders", headers=headers, json={
            "userId": user_id,
            "totalAmount": float(cart_data["subtotal"]),
            "notes": "Please make it extra hot!"
        })
        if order_res.status_code == 201:
            p("Order Placed Successfully", order_res.json())
        else:
            print(f"Failed to place order: {order_res.status_code} - {order_res.text}")

if __name__ == "__main__":
    asyncio.run(main())
