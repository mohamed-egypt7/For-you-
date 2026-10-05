import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# ضع توكن البوت الخاص بك هنا
TOKEN = "YOUR_BOT_TOKEN_HERE"

# قاعدة بيانات الصفحات (يمكنك تعديلها أو ربطها بملف json دائم)
pages_db = {
    "mok": {
        "name": "محمد ياسر",
        "password": "123",
        "message": "أهلاً بك يا مهندس محمد في رسالتك السرية",
    }
}


# أمر البداية وعرض لوحة التحكم بالأزرار
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  keyboard = []
  for slug, data in pages_db.items():
    keyboard.append([
        InlineKeyboardButton(
            f"📄 {data['name']} ({slug})", callback_data=f"view_{slug}"
        ),
        InlineKeyboardButton(f"🗑️ حذف", callback_data=f"del_{slug}"),
    ])

  keyboard.append(
      [InlineKeyboardButton("➕ إضافة صفحة جديدة", callback_data="add_page")]
  )
  reply_markup = InlineKeyboardMarkup(keyboard)

  await update.message.reply_text(
      "🎛️ *لوحة تحكم النظام (تيليجرام):*\nاختر الإجراء المطلوبة:",
      reply_markup=reply_markup,
      parse_mode="Markdown",
  )


# إدارة ضغط الأزرار التفاعلية
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  query = update.callback_query
  await query.answer()
  data = query.data

  if data.startswith("view_"):
    slug = data.split("_")[1]
    page = pages_db.get(slug)
    if page:
      msg = (
          f"📄 *تفاصيل الصفحة:*\n- المعرف: `{slug}`\n- الاسم:"
          f" {page['name']}\n- الباسورد: `{page['password']}`\n- الرسالة:"
          f" {page['message']}"
      )
      await query.edit_message_text(text=msg, parse_mode="Markdown")

  elif data.startswith("del_"):
    slug = data.split("_")[1]
    if slug in pages_db:
      del pages_db[slug]
      await query.edit_message_text(
          text=f"✅ تم حذف الصفحة ({slug}) بنجاح!\nاضغط /start للرجوع للقائمة."
      )

  elif data == "add_page":
    await query.edit_message_text(
        text=(
            "➕ لإضافة صفحة جديدة، أرسل الأمر بهذا الشكل:\n`/new"
            " slug|الاسم|الباسورد|الرسالة`"
        ),
        parse_mode="Markdown",
    )


# أمر إضافة صفحة سريعة عبر التيليجرام
async def new_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
  try:
    text = " ".join(context.args)
    slug, name, password, message = text.split("|")
    pages_db[slug.strip()] = {
        "name": name.strip(),
        "password": password.strip(),
        "message": message.strip(),
    }
    await update.message.reply_text(
        f"✅ تمت إضافة صفحة ({name.strip()}) بنجاح! اطلب /start لعرض القائمة."
    )
  except Exception:
    await update.message.reply_text(
        "❌ خطأ في الصيغة. استخدم الأمر هكذا:\n`/new"
        " slug|الاسم|الباسورد|الرسالة`",
        parse_mode="Markdown",
    )


def main():
  app = ApplicationBuilder().token(TOKEN).build()
  app.add_handler(CommandHandler("start", start))
  app.add_handler(CommandHandler("new", new_page))
  app.add_handler(CallbackQueryHandler(button_handler))

  print("بوت تيليجرام يعمل الآن بكامل الصلاحيات والأزرار...")
  app.run_polling()


if __name__ == "__main__":
  import asyncio

  asyncio.run(main())
