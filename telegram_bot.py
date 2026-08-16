import asyncio
import os
import logging
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

from ai_client import ask_ai

# Configure logging
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO").upper(),
                    format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
# Optional: restrict bot to a specific chat/user id
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

if not TELEGRAM_TOKEN:
    logger.error("TELEGRAM_TOKEN not set in environment. Please set it and restart the bot.")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "مرحباً! أنا بوت ذكاء صناعي. أرسل أي رسالة وسأرد بالإجابة المولّدة بواسطة نموذج الذكاء الصناعي.")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("اكتب أي نص وسأرسله لواجهة الـ AI وأعيد الناتج. يمكن استخدام /start للبدء.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Optional access control
    if ADMIN_CHAT_ID and str(update.effective_chat.id) != str(ADMIN_CHAT_ID):
        logger.warning("Ignoring message from unauthorized chat %s", update.effective_chat.id)
        return

    user_text = update.message.text
    if not user_text:
        return

    # Send typing action
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    loop = asyncio.get_running_loop()
    try:
        # ask_ai is blocking (requests); run it in default executor to avoid blocking the event loop
        answer = await loop.run_in_executor(None, ask_ai, user_text)
        # Send the answer (truncate if too long)
        if len(answer) > 4096:
            # Telegram message limit ~4096 chars
            for i in range(0, len(answer), 4000):
                await update.message.reply_text(answer[i:i+4000])
        else:
            await update.message.reply_text(answer)
    except Exception as e:
        logger.exception("Error while processing message: %s", e)
        await update.message.reply_text(f"حدث خطأ عند طلب الذكاء الصناعي: {e}")


def main() -> None:
    if not TELEGRAM_TOKEN:
        raise SystemExit("TELEGRAM_TOKEN is required in environment")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting Telegram bot (polling)...")
    app.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
