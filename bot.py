import asyncio
import logging
import os
from aiohttp import web
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from game import init_db, api_start, api_answer, api_me, api_leaderboard, configure_channel, update_channel_post

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("brainsir")
BOT_TOKEN = os.environ["BOT_TOKEN"]
WEBAPP_URL = os.environ["WEBAPP_URL"].rstrip("/")
PORT = int(os.environ.get("PORT", "8080"))
CHANNEL_ID = os.environ.get("CHANNEL_ID", "@brainsir")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.effective_user.first_name or "игрок"
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🧠 НАЧАТЬ ИГРУ", web_app=WebAppInfo(url=WEBAPP_URL))
    ]])
    await update.effective_message.reply_text(
        f"Привет, {name}! Это BRAINSIR.\n\n500 вопросов. 15 секунд на каждый.\nОдна ошибка — и игра окончена. Проверь свой разум!",
        reply_markup=keyboard
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_message.reply_text(
        "BRAINSIR — интеллектуальная игра: 500 вопросов, 4 варианта ответа, "
        "15 секунд на каждый. Ошибка или тайм-аут завершают игру. Нажми /start."
    )

async def main():
    await init_db()
    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_cmd))
    await bot_app.initialize()
    configure_channel(bot_app.bot, WEBAPP_URL, CHANNEL_ID)
    await bot_app.start()
    await update_channel_post()
    await bot_app.updater.start_polling(drop_pending_updates=True)

    site_app = web.Application()
    site_app.router.add_get("/", lambda r: web.FileResponse("static/index.html"))
    site_app.router.add_get("/health", lambda r: web.json_response({"ok": True, "app": "BRAINSIR"}))
    site_app.router.add_post("/api/start", api_start)
    site_app.router.add_post("/api/answer", api_answer)
    site_app.router.add_post("/api/me", api_me)
    site_app.router.add_get("/api/leaderboard", api_leaderboard)
    site_app.router.add_static("/static/", "static")
    runner = web.AppRunner(site_app)
    await runner.setup()
    await web.TCPSite(runner, "0.0.0.0", PORT).start()
    log.info("BRAINSIR запущен на порту %s", PORT)
    try:
        await asyncio.Event().wait()
    finally:
        await runner.cleanup()
        await bot_app.updater.stop()
        await bot_app.stop()
        await bot_app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
