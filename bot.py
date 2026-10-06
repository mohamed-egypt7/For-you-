import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

BOT_TOKEN = "8989450747:AAFQ56vM9mniwelDaqf5zqc76J2f3zorpE0"
ADMIN_CHAT_ID = "8718173410"

GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxAPL-k0nOCQugrFW0u8WaudCjftB5_qtQroUn03QbNHp0wdzvYopdnFZP3CUroTdvfRA/exec"
VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # 1. رد الأدمن على الزائر من التليجرام
    if str(message.chat_id) == ADMIN_CHAT_ID and message.reply_to_message:
        original_text = message.reply_to_message.text
        admin_reply = message.text

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
        return

    # 2. توليد الرابط الجديد على Vercel للزوار/المستخدمين
    user_text = message.text
    recipient_name = user_text.strip()
    direct_link = f"{VERCEL_BASE_URL}/index.html?to={recipient_name}"
    
    response_msg = (
        "✅ تمت الإضافة وتحديث الموقع بنجاح!\n\n"
        f"👤 لمن: {recipient_name}\n"
        f"🔗 الرابط المباشر:\n{direct_link}\n\n"
        "القائمة الرئيسية"
    )
    
    await message.reply_text(response_msg)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 البوت يعمل الآن ومربوط بـ Vercel...")
    app.run_polling()

if __name__ == "__main__":
    main()
