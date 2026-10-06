import json
import requests
import urllib.parse
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, ConversationHandler, filters

BOT_TOKEN = "8989450747:AAFQ56vM9mniwelDaqf5zqc76J2f3zorpE0"
ADMIN_CHAT_ID = "8718173410"

VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

# تعريف خطوات المحادثة خطوة بخطوة
NAME, PASSWORD, TITLE, LINK = range(4)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 أهلاً بيك! هنمشي مع بعض خطوة بخطوة.\n\n"
        "1️⃣ أولاً: أرسل **الاسم**:"
    )
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("2️⃣ تمام! الآن أرسل **الباسورد**:")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("3️⃣ رائع! الآن أرسل **عنوان الأغنية**:")
    return TITLE

async def get_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text.strip()
    await update.message.reply_text("4️⃣ أخيراً! أرسل **رابط الأغنية**:")
    return LINK

async def get_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()
    name = context.user_data.get('name', '')
    password = context.user_data.get('password', '')
    title = context.user_data.get('title', '')

    # تشفير البيانات لضمان سلامة الرابط على Vercel
    safe_name = urllib.parse.quote(name)
    safe_pass = urllib.parse.quote(password)
    safe_title = urllib.parse.quote(title)
    safe_link = urllib.parse.quote(link)

    direct_link = f"{VERCEL_BASE_URL}/index.html?to={safe_name}&pass={safe_pass}&title={safe_title}&link={safe_link}"

    response_msg = (
        "✅ تم جمع البيانات وتوليد الرابط بنجاح:\n\n"
        f"👤 الاسم: {name}\n"
        f"🔒 الباسورد: {password}\n"
        f"🎵 الأغنية: {title}\n\n"
        f"🔗 الرابط المباشر:\n{direct_link}\n\n"
        "للبدء من جديد، أرسل /start"
    )
    await update.message.reply_text(response_msg)
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ تم الإلغاء. للبدء من جديد أرسل /start")
    return ConversationHandler.END

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_password)],
            TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_title)],
            LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_link)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    
    app.add_handler(conv_handler)
    print("🤖 البوت يعمل الآن بنظام الخطوة بخطوة...")
    app.run_polling()

if __name__ == "__main__":
    main()
