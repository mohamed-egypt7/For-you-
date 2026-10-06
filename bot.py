import json
import requests
import urllib.parse
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8989450747:AAFQ56vM9mniwelDaqf5zqc76J2f3zorpE0"
ADMIN_CHAT_ID = "8718173410"

VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return

    text = message.text.strip()
    
    # لو الرسالة أمر /start
    if text.startswith('/start'):
        await message.reply_text(
            "👋 أهلاً بيك! أرسل البيانات دفعة واحدة بالترتيب ده:\n"
            "الاسم | الباسورد | عنوان الأغنية | رابط الأغنية\n\n"
            "مثال:\n"
            "أحمد 1234 تملي معاك https://youtube.com/..."
        )
        return

    # استقبال البيانات مقسومة بـ | أو مسافات
    parts = [p.strip() for p in text.split('|')]
    if len(parts) < 4:
        parts = text.split()
        
    if len(parts) >= 4:
        name, password, title, link = parts[0], parts[1], parts[2], " ".join(parts[3:])
        
        safe_name = urllib.parse.quote(name)
        safe_pass = urllib.parse.quote(password)
        safe_title = urllib.parse.quote(title)
        safe_link = urllib.parse.quote(link)

        # رابط Vercel المتكامل الذي يحتوي على كل البيانات
        direct_link = f"{VERCEL_BASE_URL}/index.html?to={safe_name}&pass={safe_pass}&title={safe_title}&link={safe_link}"

        response_msg = (
            "✅ تم توليد الرابط المباشر بنجاح:\n\n"
            f"👤 الاسم: {name}\n"
            f"🔒 الباسورد: {password}\n"
            f"🎵 الأغنية: {title}\n\n"
            f"🔗 الرابط:\n{direct_link}"
        )
        await message.reply_text(response_msg)
    else:
        await message.reply_text("⚠️ يرجى إرسال البيانات الأربعة صحيحة (الاسم، الباسورد، عنوان الأغنية، والرابط).")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("🤖 البوت يعمل الآن بشكل مباشر مع تليجرام...")
    app.run_polling()

if __name__ == "__main__":
    main()
