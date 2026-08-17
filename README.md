# Telegram AI Bot (Arabic)

بوت تليجرام بسيط يربط بين Telegram و OpenAI ويُجيب بالعربية. تمت إضافة ذاكرة محادثة بسيطة مبنية على SQLite.

## المتطلبات
- Python 3.10+
- مفتاح Telegram Bot من BotFather (TELEGRAM_TOKEN)
- مفتاح OpenAI (OPENAI_API_KEY)

## تشغيل محلياً
1. انسخ الملفات لمجلد.
2. أنشئ ملف `.env` داخل المجلد بناءً على `.env.example` واعدل القيم:
   TELEGRAM_TOKEN=توكن_البوت_من_BotFather
   OPENAI_API_KEY=مفتاح_OpenAI
   # اختياري
   OPENAI_MODEL=gpt-3.5-turbo
   MAX_TOKENS=500
   TEMPERATURE=0.7
   MAX_MEMORY_MESSAGES=10
3. ثبت الحزم:
   pip install -r requirements.txt
4. شغّل البوت:
   python main.py

## أوامر مفيدة داخل البوت
- /start: بداية المحادثة
- /help: شرح قصير
- /clear: مسح ذاكرة المحادثة لهذه الدردشة

## تشغيل بـ Docker
1. بناء الصورة:
   docker build -t telegram-ai-bot .
2. تشغيل الحاوية:
   docker run --env-file .env telegram-ai-bot

## ملاحظات أمان
- لا ترفع مفاتيحك للمستودع. احتفظ بها في متغيرات بيئية أو Secrets في المزود.
- ذاكرة المحادثة تحفظ نصوص المستخدم والردود في ملف SQLite `memory.db` داخل الحاوية/السيرفر — لو تحتاج خصوصية أعلى، استخدم قاعدة بيانات مُدارة أو امسح البيانات دورياً.

## إمكانيات لاحقة
- تقليم الذاكرة بناءً على عدد التوكنز بدل عدد الرسائل.
- تخزين في Postgres/Redis بدل SQLite ليدعم التوسع.
- فلترة أو تدقيق محتوى قبل الحفظ (moderation).
