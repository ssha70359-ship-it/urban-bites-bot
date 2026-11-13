import os
import random
import aiohttp

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

MENU_TEXT_SUMMARY = "\n".join(
    [f"- {i['name']} ({i['category']}): ${i['price']} — {i['desc']}" for i in MENU_ITEMS]
)


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
        "note": delivery_address_or_note,
        "payment_info": "Demo Mode: Payment is simulated via Stripe / Telegram Stars / Cash on Delivery."
    }


TOOLS_DECLARATION = [
    {
        "function_declarations": [
            {
                "name": "search_menu_items",
                "description": "Filter menu items by category and maximum price in USD.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "category": {"type": "STRING", "description": "Burgers, Pizza, Sides, Drinks, Desserts, or all"},
                        "max_price": {"type": "NUMBER", "description": "Maximum price in USD"}
                    }
                }
            },
            {
                "name": "calculate_combo_price",
                "description": "Calculate exact total price in USD for multiple items.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "item_names": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "quantities": {"type": "ARRAY", "items": {"type": "INTEGER"}}
                    },
                    "required": ["item_names", "quantities"]
                }
            },
            {
                "name": "create_chat_order",
                "description": "Register and confirm a customer order when they confirm or ask to pay/checkout.",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                        "customer_items": {"type": "STRING", "description": "Summary of ordered items and quantities"},
                        "total_price": {"type": "NUMBER", "description": "Total order price in USD"},
                        "delivery_address_or_note": {"type": "STRING", "description": "Customer address or payment/delivery note"}
                    },
                    "required": ["customer_items", "total_price"]
                }
            }
        ]
    }
]

SYSTEM_INSTRUCTION = f"""
You are the official AI Waiter & Sales Agent for "Urban Bites Store" (an interactive Telegram Mini App & Restaurant).

OFFICIAL MENU:
{MENU_TEXT_SUMMARY}

RULES:
1. Reply in the same language the user writes in (English, Uzbek, or Russian).
2. You already know the full menu above — answer simple menu/price questions directly in 1 step without calling a tool unless complex filtering is needed.
3. When the user confirms an order or asks how/where to pay ("to'lov qayerda", "tasdiqlayman", "checkout"), call `create_chat_order` to generate their official Order ID receipt and explain that in this demo, checkout works right here in chat or visually via the Mini App button below (supports Stripe, Crypto, and Telegram Stars in production).
4. Keep replies concise (3-6 short lines) with clean emojis. Do NOT use markdown asterisks (**).
"""

user_histories = {}
AVAILABLE_MODELS = []
SIMPLE_CACHE = {}


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


async def get_model_candidates(session: aiohttp.ClientSession, api_key: str) -> list[str]:
    global AVAILABLE_MODELS
    if AVAILABLE_MODELS:
        return AVAILABLE_MODELS

    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    async with session.get(list_url) as resp:
        data = await resp.json()

    raw_models = []
    for m in data.get("models", []):
        methods = m.get("supportedGenerationMethods", [])
        short_name = m.get("name", "").replace("models/", "")
        if "generateContent" in methods and "gemini" in short_name:
            if not any(skip in short_name for skip in ["tts", "image", "embedding", "aqa", "vision", "thinking"]):
                raw_models.append(short_name)

    priority = [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash-lite-preview",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
        "gemini-flash-lite-latest",
        "gemini-flash-latest",
        "gemini-3-flash-preview",
        "gemini-3-flash",
        "gemini-2.5-pro",
    ]

    ordered = [p for p in priority if p in raw_models]
    for r in raw_models:
        if r not in ordered:
            ordered.append(r)

    AVAILABLE_MODELS = ordered if ordered else ["gemini-flash-latest", "gemini-3-flash-preview"]
    return AVAILABLE_MODELS


async def get_ai_agent_response(user_id: int, user_message: str) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "⚠️ GEMINI_API_KEY topilmadi."

    history = user_histories.setdefault(user_id, [])
    if len(history) > 10:
        history[:] = history[-10:]
    while history and history[0].get("role") != "user":
        history.pop(0)

    # Agar suhbat endi boshlangan bo'lsa va bu savol avval berilgan bo'lsa, keshdan (0 limit sarflab) qaytaramiz
    norm_key = user_message.strip().lower()
    if not history and norm_key in SIMPLE_CACHE:
        cached_reply = SIMPLE_CACHE[norm_key]
        history.append({"role": "user", "parts": [{"text": user_message}]})
        history.append({"role": "model", "parts": [{"text": cached_reply}]})
        return cached_reply

    try:
        async with aiohttp.ClientSession() as session:
            models_to_try = await get_model_candidates(session, api_key)

            for model_name in models_to_try:
                working_contents = list(history) + [
                    {"role": "user", "parts": [{"text": user_message}]}
                ]
                switch_model = False

                for _ in range(4):
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                    payload = {
                        "system_instruction": {"parts": [{"text": SYSTEM_INSTRUCTION}]},
                        "contents": working_contents,
                        "tools": TOOLS_DECLARATION,
                        "generationConfig": {"temperature": 0.3}
                    }

                    async with session.post(url, json=payload) as resp:
                        data = await resp.json()

                    if "error" in data:
                        err_code = data["error"].get("code", 0)
                        err_msg = data["error"].get("message", "")
                        if err_code in (429, 404, 503) or "quota" in err_msg.lower() or "not found" in err_msg.lower():
                            switch_model = True
                            break
                        return f"⚠️ Xatolik yuz berdi: {err_msg}"

                    candidate = data.get("candidates", [{}])[0]
                    model_content = candidate.get("content", {})
                    parts = model_content.get("parts", [])

                    if not parts:
                        switch_model = True
                        break

                    working_contents.append(model_content)

                    fn_calls = [p["functionCall"] for p in parts if "functionCall" in p]
                    if not fn_calls:
                        text_parts = [p.get("text", "") for p in parts if "text" in p]
                        final_text = "\n".join(text_parts).strip().replace("**", "")

                        if not history and len(SIMPLE_CACHE) < 200:
                            SIMPLE_CACHE[norm_key] = final_text

                        history.append({"role": "user", "parts": [{"text": user_message}]})
                        history.append({"role": "model", "parts": [{"text": final_text}]})
                        return final_text

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

                    working_contents.append({"role": "user", "parts": fn_responses})

                if not switch_model:
                    break

            return (
                "⏳ Hozir AI xizmatida so'rovlar ko'p. "
                "Iltimos, 20-30 soniyadan so'ng qayta yozing yoki pastdagi Mini App tugmasidan foydalaning! 🚀"
            )

    except Exception as e:
        user_histories.pop(user_id, None)
        return f"⚠️ Bog'lanishda xatolik: {e}"