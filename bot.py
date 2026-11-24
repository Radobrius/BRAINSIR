
import asyncio
import logging
import os
from aiohttp import web
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, Update
from telegram.ext import Application, CommandHandler, ContextTypes
from game import init_db, api_start, api_answer, api_me, api_leaderboard

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("brainsir")

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Railway may occasionally pass an empty WEBAPP_URL despite a dashboard value.
# Fall back to the known public Railway domain.
WEBAPP_URL = (os.environ.get("WEBAPP_URL") or "").strip().rstrip("/")
if not WEBAPP_URL:
    WEBAPP_URL = "https://web-production-49488216.up.railway.app"

if not WEBAPP_URL.startswith(("https://", "http://")):
    raise RuntimeError("WEBAPP_URL must be a full http(s) URL")

PORT = int(os.environ.get("PORT", "8080"))


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


@web.middleware
async def no_cache_middleware(request, handler):
    response = await handler(request)
    # Always revalidate the page and static files after a Railway deployment.
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


async def main():
    await init_db()

    bot_app = Application.builder().token(BOT_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CommandHandler("help", help_cmd))

    await bot_app.initialize()
    log.info("Mini App URL configured: %s", WEBAPP_URL)

    await bot_app.start()
    await bot_app.updater.start_polling(drop_pending_updates=True)

    site_app = web.Application(middlewares=[no_cache_middleware])
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

