# Telegram AI Bot (Arabic)

بوت تليجرام بسيط يربط بين Telegram و OpenAI ويُجيب بالعربية.

## المتطلبات
- Python 3.10+
- مفتاح Telegram Bot من BotFather (TELEGRAM_TOKEN)
- مفتاح OpenAI (OPENAI_API_KEY)

## تشغيل محلياً
1. انسخ الملفات لمجلد.
2. أنشئ ملف `.env` داخل المجلد بناءً على `.env.example`.
3. ثبت الحزم:
   pip install -r requirements.txt
4. شغّل البوت:
   python main.py

## تشغيل بـ Docker
1. بناء الصورة:
   docker build -t telegram-ai-bot .
2. تشغيل الحاوية:
   docker run --env-file .env telegram-ai-bot

## ملاحظات أمان
- لا ترفع مفاتيحك للمستودع. احتفظ بها في متغيرات بيئية أو Secrets في المزود.
- إذا تريد حفظ سياق المحادثة لكل مستخدم (ذاكرة)، نقدر نضيف تخزين SQLite/Postgres مع ترشيق السياق قبل الإرسال إلى OpenAI.

## إذا أردت رفع الكود إلى GitHub
أرسل لي اسم الريبو بصيغة `owner/repo` وسأرفع الملفات على فرع `telegram-ai-bot` وأفتح PR إن رغبت.
