import asyncio
import json
import logging
import os
from aiohttp import web
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    Message,
    WebAppInfo,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from ai_agent import get_ai_agent_response

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message):
    reply_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍 Open Urban Bites Store",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ],
        resize_keyboard=True,
    )

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Launch Mini App Demo",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )

    welcome_text = (
        f"👋 <b>Welcome to Urban Bites Store Demo, {message.from_user.first_name}!</b>\n\n"
        "This is a live portfolio demonstration of a <b>Telegram Mini App (WebApp) + AI Sales Agent</b> "
        "built with <b>React (Vite) + Python (aiogram 3) + Gemini AI</b>.\n\n"
        "🛍 <b>Option 1 (Visual Store):</b> Tap the <b>'🛍 Open Urban Bites Store'</b> button below to browse products and checkout.\n"
        "🤖 <b>Option 2 (AI Waiter):</b> Simply write a message right here in the chat (e.g., <i>'What burgers do you have under $12?'</i> or <i>'Suggest a combo for $25'</i>)!"
    )

    await message.answer(welcome_text, parse_mode="HTML", reply_markup=reply_kb)
    await message.answer(
        "Or preview the interface directly via the inline button below:",
        reply_markup=inline_kb,
    )


@dp.message(F.web_app_data)
async def handle_webapp_order(message: Message):
    try:
        data = json.loads(message.web_app_data.data)
        items = data.get("items", [])
        total = data.get("total", "0.00")
        note = data.get("note", "None")

        items_list = "\n".join(
            [
                f"• <b>{item['name']}</b> x{item['qty']} — ${item['price'] * item['qty']:.2f}"
                for item in items
            ]
        )

        receipt = (
            "✅ <b>Order Successfully Received! (Demo)</b>\n\n"
            f"📦 <b>Items:</b>\n{items_list}\n\n"
            f"📝 <b>Note:</b> {note}\n"
            f"💳 <b>Total Amount:</b> <b>${total}</b>\n\n"
            "<i>In a production project, this step triggers Stripe / Crypto / Telegram Stars payment and saves the order to PostgreSQL.</i>"
        )

        await message.answer(receipt, parse_mode="HTML")

        if ADMIN_ID and ADMIN_ID.isdigit():
            user_info = (
                f"@{message.from_user.username}"
                if message.from_user.username
                else message.from_user.full_name
            )
            admin_alert = (
                f"🔔 <b>New Demo Test Alert!</b>\n"
                f"👤 <b>User:</b> {user_info} (ID: <code>{message.from_user.id}</code>)\n"
                f"💰 <b>Cart Total:</b> ${total}"
            )
            await bot.send_message(
                chat_id=int(ADMIN_ID), text=admin_alert, parse_mode="HTML"
            )

    except Exception as e:
        logging.error(f"Error parsing WebApp data: {e}")
        await message.answer("⚠️ Error processing order data.")


@dp.message(F.text & ~F.text.startswith("/"))
async def ai_waiter_handler(message: Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    reply_text = await get_ai_agent_response(message.from_user.id, message.text)

    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🚀 Launch Mini App Demo",
                    web_app=WebAppInfo(url=WEBAPP_URL),
                )
            ]
        ]
    )
    await message.answer(reply_text, reply_markup=inline_kb)


# Render port tekshiruvi uchun mitti veb-server
async def health_check(request):
    return web.Response(text="Urban Bites Bot is running!")


async def start_web_server():
    app = web.Application()
    app.router.add_get("/", health_check)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Health check server listening on port {port}")


async def main():
    logging.basicConfig(level=logging.INFO)
    await start_web_server()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())