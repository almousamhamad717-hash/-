#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai
from dotenv import load_dotenv

load_dotenv()

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Env
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.error("Missing TELEGRAM_TOKEN or OPENAI_API_KEY environment variables.")
    raise SystemExit("Set TELEGRAM_TOKEN and OPENAI_API_KEY first")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أنا بوت ذكي يرد بالعربية. ارسل لي أي رسالة وسأرد عليك."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل نصّاً وسيجيبك البوت. استخدم /start للبدء."
    )

async def call_openai(user_text: str) -> str:
    # Run blocking network call in thread to avoid blocking the event loop
    def _sync_call():
        return openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "أنت مساعد ودود يتحدث العربية، اجب باختصار ووضوح بالعربية إذا طلب المستخدم ذلك."},
                {"role": "user", "content": user_text}
            ],
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )
    try:
        resp = await asyncio.to_thread(_sync_call)
        return resp.choices[0].message.content.strip()
    except Exception as e:
        logger.exception("OpenAI API error")
        return "حصل خطأ عند الاتصال بخدمة الذكاء الصناعي. حاول مرة ثانية لاحقاً."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    logger.info("Message from %s: %s", chat_id, text[:200])

    await update.message.chat.action("typing")
    reply = await call_openai(text)
    await update.message.reply_text(reply)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
