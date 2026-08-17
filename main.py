#!/usr/bin/env python3
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai
from dotenv import load_dotenv

from memory import MemoryStore

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
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", "10"))  # per user (pairs)

if not TELEGRAM_TOKEN or not OPENAI_API_KEY:
    logger.error("Missing TELEGRAM_TOKEN or OPENAI_API_KEY environment variables.")
    raise SystemExit("Set TELEGRAM_TOKEN and OPENAI_API_KEY first")

openai.api_key = OPENAI_API_KEY

# Initialize memory store (SQLite)
memory = MemoryStore(db_path=os.getenv("MEMORY_DB", "memory.db"), max_messages=MAX_MEMORY_MESSAGES)
memory.init_db()

SYSTEM_PROMPT = "أنت مساعد ودود يتحدث العربية، اجب باختصار ووضوح بالعربية إذا طلب المستخدم ذلك."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحباً! أنا بوت ذكي يرد بالعربية. لدي ذاكرة محادثة بسيطة. ارسل لي أي رسالة وسأرد عليك."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "أرسل نصّاً وسيجيبك البوت. استخدم /start للبدء. لإفراغ الذاكرة استخدم /clear."
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    memory.clear_history(chat_id)
    await update.message.reply_text("تم حذف ذاكرة المحادثة لهذه الدردشة.")

async def call_openai_with_memory(chat_id: str, user_text: str) -> str:
    # Build messages: system, memory history, current user
    history = memory.get_history(chat_id)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    # Run blocking network call in thread to avoid blocking the event loop
    def _sync_call():
        return openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=messages,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE
        )

    try:
        resp = await asyncio.to_thread(_sync_call)
        assistant_reply = resp.choices[0].message.content.strip()
        return assistant_reply
    except Exception:
        logger.exception("OpenAI API error")
        return "حصل خطأ عند الاتصال بخدمة الذكاء الصناعي. حاول مرة ثانية لاحقاً."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = str(update.effective_chat.id)
    logger.info("Message from %s: %s", chat_id, text[:200])

    await update.message.chat.action("typing")

    # Save user message to memory
    memory.add_message(chat_id, "user", text)

    reply = await call_openai_with_memory(chat_id, text)

    # Save assistant reply to memory
    memory.add_message(chat_id, "assistant", reply)

    await update.message.reply_text(reply)


def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Starting bot with memory...")
    app.run_polling()

if __name__ == "__main__":
    main()
