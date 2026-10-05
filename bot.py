import json
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# 1. البيانات الخاصة بالبوت
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"

# 2. رابط Google Apps Script الخاص بجوجل شيت
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxAPL-k0nOCQugrFW0u8WaudCjftB5_qtQroUn03QbNHp0wdzvYopdnFZP3CUroTdvfRA/exec"

# 3. الرابط الأساسي الجديد لموقعك على Vercel
VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # ----------------------------------------------------
    # الحالة الأولى: رد الأدمن عبر التليجرام لإرسال الرد لجوجل شيت
    # ----------------------------------------------------
    if str(message.chat_id) == ADMIN_CHAT_ID and message.reply_to_message:
        original_text = message.reply_to_message.text
        admin_reply = message.text

        # استخراج الـ IP الخاص بالزائر من نص الرسالة القديمة
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

    # ----------------------------------------------------
    # الحالة الثانية: توليد رابط الصفحة الجديد للمستخدم على Vercel
    # ----------------------------------------------------
    # ملاحظة: إذا كان البوت يجمع بيانات من الزائر لإنشاء صفحة،
    # سنقوم بتركيب الرابط الجديد على Vercel بدلاً من GitHub Pages.
    user_text = message.text
    
    # مثال لتوليد الرابط بنفس الصيغة المطلوبة في الصورة:
    # https://for-you-oot4.vercel.app/index.html?to=اسم_المستلم
    recipient_name = user_text.strip()  # أو المتغير الذي تخزن فيه الاسم
    
    # بناء رابط Vercel المباشر بدلاً من github.io
    direct_link = f"{VERCEL_BASE_URL}/index.html?to={recipient_name}"
    
    response_msg = (
        "✅ تمت الإضافة وتحديث الموقع بنجاح!\n\n"
        f"👤 لمن: {recipient_name}\n"
        f"🔗 الرابط المباشر:\n{direct_link}\n\n"
        "ال قائمة الرئيسية"
    )
    
    # إرسال النتيجة للمستخدم
    # await message.reply_text(response_msg)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 بوت تليجرام يعمل الآن ومربوط بـ Vercel و Google Sheets...")
    app.run_polling()

if __name__ == "__main__":
    main()
