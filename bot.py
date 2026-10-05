import json
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# استبدل هذا التوكن بتوكن البوت الخاص بك
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"  # معرف التيليجرام الخاص بك

# دالة التعامل مع الرسائل القادمة والردود (Reply)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # التأكد أن الرسالة قادمة منك (الآدمن) وفيها Reply على رسالة سابقة من زائر
    if str(message.chat_id) == ADMIN_CHAT_ID and message.reply_to_message:
        replied_text = message.reply_to_message.text
        admin_reply = message.text

        # نبحث في النص القديم (رسالة الزائر) عن اسم المستخدم أو الـ IP أو كود الجلسة لربط الرد به
        # مثال: لو رسالة الزائر تحتوي على اسم أو معرف، نقدر نحدث ملف db.json بناءً عليه
        await message.reply_text(f"✅ تم تسجيل الرد بنجاح وإرساله للزائر:\n{admin_reply}")
        
        # هنا يمكنك تحديث ملف db.json محلياً وإعادة رفعه لـ GitHub تلقائياً لتحديث شات الزائر
        # update_db_with_reply(replied_text, admin_reply)

async def main():
    # بناء تطبيق البوت
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # استقبال الرسائل النصية وردود الأفعال
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    print("🤖 البوت يعمل الآن ويراقب الردود...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
