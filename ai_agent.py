import os
import random
import aiohttp

# Urban Bites Store menyusi (Mini App bilan bir xil baza)
MENU_ITEMS = [
    {"id": 1, "name": "Classic Smash Burger", "category": "Burgers", "price": 8.99, "desc": "Double beef patty, cheddar, house sauce"},
    {"id": 2, "name": "Truffle Mushroom Burger", "category": "Burgers", "price": 11.49, "desc": "Swiss cheese, roasted mushrooms, truffle mayo"},
    {"id": 3, "name": "Spicy Jalapeno Burger", "category": "Burgers", "price": 9.99, "desc": "Pepper jack cheese, fresh jalapenos, chipotle"},
    {"id": 4, "name": "Crispy Chicken Burger", "category": "Burgers", "price": 8.49, "desc": "Buttermilk fried chicken, pickles, coleslaw"},
    {"id": 5, "name": "Margherita Artisan Pizza", "category": "Pizza", "price": 12.99, "desc": "San Marzano tomatoes, fresh mozzarella, basil"},
    {"id": 6, "name": "Pepperoni Hot Honey Pizza", "category": "Pizza", "price": 14.99, "desc": "Double pepperoni, mozzarella, spicy honey drizzle"},
    {"id": 7, "name": "BBQ Chicken Pizza", "category": "Pizza", "price": 15.49, "desc": "Grilled chicken, red onions, smoky BBQ sauce"},
    {"id": 8, "name": "Loaded Cheese Fries", "category": "Sides", "price": 5.49, "desc": "Crispy fries, melted cheddar, bacon bits"},
    {"id": 9, "name": "Crispy Onion Rings", "category": "Sides", "price": 4.99, "desc": "Beer-battered onion rings with ranch dip"},
    {"id": 10, "name": "6pc Buffalo Wings", "category": "Sides", "price": 7.99, "desc": "Spicy buffalo glaze, celery, blue cheese dip"},
    {"id": 11, "name": "Fresh Berry Lemonade", "category": "Drinks", "price": 3.99, "desc": "Homemade lemonade with muddled berries"},
    {"id": 12, "name": "Iced Caramel Macchiato", "category": "Drinks", "price": 4.49, "desc": "Espresso, cold milk, vanilla & caramel"},
    {"id": 13, "name": "Classic Cola (330ml)", "category": "Drinks", "price": 2.49, "desc": "Chilled can"},
    {"id": 14, "name": "New York Cheesecake", "category": "Desserts", "price": 6.49, "desc": "Creamy cheesecake with strawberry topping"},
    {"id": 15, "name": "Warm Chocolate Lava Cake", "category": "Desserts", "price": 6.99, "desc": "Molten chocolate center with vanilla ice cream"},
]

# ==========================================
# 1. AI AGENT FUNKSIYALARI (TOOLS)
# ==========================================

def search_menu_items(category: str = "all", max_price: float = 100.0) -> list[dict]:
    results = []
    for item in MENU_ITEMS:
        cat_match = category.lower() == "all" or item["category"].lower() == category.lower()
        price_match = item["price"] <= float(max_price)
        if cat_match and price_match:
            results.append(item)
    return results


def calculate_combo_price(item_names: list[str], quantities: list[int]) -> dict:
    total = 0.0
    found_items = []
    not_found = []

    for name, qty in zip(item_names, quantities):
        matched = next((i for i in MENU_ITEMS if name.lower() in i["name"].lower()), None)
        if matched:
            qty_int = int(qty)
            subtotal = round(matched["price"] * qty_int, 2)
            total += subtotal
            found_items.append({
                "name": matched["name"],
                "qty": qty_int,
                "unit_price": matched["price"],
                "subtotal": subtotal
            })
        else:
            not_found.append(name)

    return {
        "items": found_items,
        "total_usd": round(total, 2),
        "not_found": not_found
    }


def create_chat_order(customer_items: str, total_price: float, delivery_address_or_note: str = "Standard Delivery") -> dict:
    order_id = f"UB-AI-{random.randint(1000, 9999)}"
    return {
        "status": "SUCCESS",
        "order_id": order_id,
        "items_summary": customer_items,
        "total_usd": f"${float(total_price):.2f}",
        "note": delivery_address_or_note
    }


# Gemini API uchun Tool (Function Calling) tavsiflari
TOOLS_DECLARATION = [
    {
        "function_declarations": [
            {
                "name": "search_menu_items",
                "description": "Search menu items by category (Burgers, Pizza, Sides, Drinks, Desserts, or all) and maximum price in USD.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "category": {"type": "STRING", "description": "Category name: Burgers, Pizza, Sides, Drinks, Desserts, or all"},
                        "max_price": {"type": "NUMBER", "description": "Maximum price in USD"}
                    }
                }
            },
            {
                "name": "calculate_combo_price",
                "description": "Calculate exact total price in USD for a list of menu item names and their quantities.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "item_names": {"type": "ARRAY", "items": {"type": "STRING"}, "description": "Names of the items"},
                        "quantities": {"type": "ARRAY", "items": {"type": "INTEGER"}, "description": "Quantity for each item"}
                    },
                    "required": ["item_names", "quantities"]
                }
            },
            {
                "name": "create_chat_order",
                "description": "Register and confirm a customer order ONLY after the customer explicitly confirms they want to place the order.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "customer_items": {"type": "STRING", "description": "Summary of ordered items and quantities"},
                        "total_price": {"type": "NUMBER", "description": "Total order price in USD"},
                        "delivery_address_or_note": {"type": "STRING", "description": "Customer address or delivery note"}
                    },
                    "required": ["customer_items", "total_price"]
                }
            }
        ]
    }
]

SYSTEM_INSTRUCTION = """
You are the official AI Waiter & Sales Agent for "Urban Bites Store" (an interactive Telegram Mini App & Restaurant).
Your job is to help customers pick food, suggest combos within their budget, calculate exact totals, and register orders in chat.

RULES:
1. Reply in the same language the user writes in (English, Uzbek, or Russian).
2. Use `search_menu_items` to check the menu or filter by budget/category.
3. Use `calculate_combo_price` to compute exact totals.
4. Use `create_chat_order` ONLY when the user confirms they want to place the order.
5. Keep replies concise (3-6 short lines) with clean emojis. Remind them they can also tap the Mini App button below for the visual catalog.
"""

# Foydalanuvchilar suhbat xotirasi
user_histories = {}


def execute_local_tool(fn_name: str, args: dict):
    if fn_name == "search_menu_items":
        return search_menu_items(
            category=args.get("category", "all"),
            max_price=args.get("max_price", 100.0)
        )
    elif fn_name == "calculate_combo_price":
        return calculate_combo_price(
            item_names=args.get("item_names", []),
            quantities=args.get("quantities", [])
        )
    elif fn_name == "create_chat_order":
        return create_chat_order(
            customer_items=args.get("customer_items", ""),
            total_price=args.get("total_price", 0.0),
            delivery_address_or_note=args.get("delivery_address_or_note", "Standard Delivery")
        )
    return {"error": f"Unknown function: {fn_name}"}


async def get_ai_agent_response(user_id: int, user_message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ GEMINI_API_KEY topilmadi. Iltimos, .env fayliga API kalitni qo'shing."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"

    history = user_histories.setdefault(user_id, [])
    history.append({"role": "user", "parts": [{"text": user_message}]})

    # Xotira juda uzayib ketmasligi uchun oxirgi 12 ta qadamni saqlaymiz
    if len(history) > 12:
        history[:] = history[-12:]

    try:
        async with aiohttp.ClientSession() as session:
            for _ in range(3):
                payload = {
                    "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
                    "contents": history,
                    "tools": TOOLS_DECLARATION,
                    "generationConfig": {"temperature": 0.3}
                }

                async with session.post(url, json=payload) as resp:
                    data = await resp.json()

                if "error" in data:
                    history.pop()
                    return f"⚠️ Gemini API xatosi: {data['error'].get('message', 'Nomalum xato')}"

                candidate = data.get("candidates", [{}])[0]
                model_content = candidate.get("content", {})
                parts = model_content.get("parts", [])

                if not parts:
                    return "🍔 Kechirasiz, javobni shakllantirib bo'lmadi. Qayta yozib ko'ring!"

                # Model javobini xotiraga qo'shamiz
                history.append(model_content)

                # Model funksiya (Tool) chaqirganini tekshiramiz
                fn_calls = [p["functionCall"] for p in parts if "functionCall" in p]
                if not fn_calls:
                    text_parts = [p.get("text", "") for p in parts if "text" in p]
                    return "\n".join(text_parts).strip()

                # Chaqirilgan funksiyalarni bajarib, natijasini Gemini'ga qaytaramiz
                fn_responses = []
                for call in fn_calls:
                    fn_name = call["name"]
                    fn_args = call.get("args", {})
                    result = execute_local_tool(fn_name, fn_args)
                    fn_responses.append({
                        "functionResponse": {
                            "name": fn_name,
                            "response": {"result": result}
                        }
                    })

                history.append({"role": "user", "parts": fn_responses})

            return "✅ Buyurtma ma'lumotlari qayta ishlandi!"

    except Exception as e:
        user_histories.pop(user_id, None)
        return f"⚠️ AI Agent bilan bog'lanishda xatolik: {e}"