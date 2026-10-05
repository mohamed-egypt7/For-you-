import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# التوكنات ومعرفات الآدمن
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"

# رابط الـ Web App الخاص بجوجل شيت
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxAPL-k0nOCQugrFW0u8WaudCjftB5_qtQroUn03QbNHp0wdzvYopdnFZP3CUroTdvfRA/exec"

# الرابط الأساسي لمنصة Vercel للملفات
VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # 1. حالة رد الآدمن على رسالة زائر عبر التليجرام
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
            try:
                payload = {
                    "ip": visitor_ip,
                    "message": "admin_reply",
                    "reply": admin_reply
                }
                requests.post(GOOGLE_SCRIPT_URL, json=payload)
                await message.reply_text(f"✅ تم إرسال الرد للزائر بنجاح:\n{admin_reply}")
            except Exception as e:
                await message.reply_text(f"❌ حدث خطأ أثناء الإرسال لجوجل شيت: {e}")
        else:
            await message.reply_text("⚠️ لم يتم التعرف على الـ IP في هذه الرسالة.")
            
    # 2. إذا أردت إرسال رابط ملف جديد للمستخدم (مثال توضيحي لطريقة بناء رابط Vercel)
    # يمكنك استخدام هذه الصيغة كلما أنشأ البوت صفحة جديدة ورفعها لمستودع جيت هاب:
    # file_name = "example.html"  # ضع هنا اسم الملف الذي تم إنشاؤه
    # final_page_url = f"{VERCEL_BASE_URL}/{file_name}"
    # await message.reply_text(f"🚀 رابط صفحتك الجديد على Vercel:\n{final_page_url}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 بوت تليجرام يعمل الآن ومربوط بمنصة Vercel و Google Sheets...")
    app.run_polling()

if __name__ == "__main__":
    main()
