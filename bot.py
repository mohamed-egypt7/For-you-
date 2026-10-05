import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# التوكنات ومعرفات الآدمن
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"

# رابط الـ Web App الخاص بجوجل شيت
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxAPL-k0nOCQugrFW0u8WaudCjftB5_qtQroUn03QbNHp0wdzvYopdnFZP3CUroTdvfRA/exec"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # التأكد أن الرسالة من الآدمن ومعها Reply على رسالة سابقة
    if str(message.chat_id) == ADMIN_CHAT_ID and message.reply_to_message:
        original_text = message.reply_to_message.text
        admin_reply = message.text

        # استخراج الـ IP الخاص بالزائر من النص القديم للرسالة
        visitor_ip = None
        for line in original_text.split('\n'):
            if "IP:" in line:
                visitor_ip = line.split(":")[-1].strip()
                break

        if visitor_ip:
            # إرسال الرد لجوجل شيت أوتوماتيك
            try:
                payload = {
                    "ip": visitor_ip,
                    "message": "admin_reply", # علامة عشان السكريبت يعرف إنه رد أدمن
                    "reply": admin_reply
                }
                requests.post(GOOGLE_SCRIPT_URL, json=payload)
                
                await message.reply_text(f"✅ تم إرسال الرد للزائر بنجاح:\n{admin_reply}")
            except Exception as e:
                await message.reply_text(f"❌ حدث خطأ أثناء الإرسال لجوجل شيت: {e}")
        else:
            await message.reply_text("⚠️ لم يتم التعرف على IP الزائر في هذه الرسالة.")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 بوت تليجرام يعمل الآن ومربوط بـ Google Sheets...")
    app.run_polling()

if __name__ == "__main__":
    main()
