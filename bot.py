import json
import base64
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# ====================================================
# 1. البيانات والإعدادات الأساسية
# ====================================================
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"

# بيانات GitHub لتحديث ملف db.json تلقائياً
GITHUB_REPO = "mohamed-egypt7/For-you-"
# ضع توكن جيت هاب الخاص بك هنا (إذا كنت تستخدم GitHub API)
GITHUB_TOKEN = "ضع_توكن_جيت_هاب_هنا"

# 🟢 الرابط المباشر والجديد لمنصة Vercel
VERCEL_BASE_URL = "https://for-you-oot4.vercel.app"

# رابط Google Apps Script لردود الشيت
GOOGLE_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbxAPL-k0nOCQugrFW0u8WaudCjftB5_qtQroUn03QbNHp0wdzvYopdnFZP3CUroTdvfRA/exec"

# مراحل إدخال البيانات لإنشاء صفحة جديدة
NAME, SLUG, PASSWORD, MESSAGE_TEXT, SONG_TITLE, SONG_LINK = range(6)


# ====================================================
# 2. دالة تحديث ملف db.json على GitHub
# ====================================================
def update_db_on_github(slug, new_entry):
    """تحديث ملف db.json وإضافة البيانات بالرابط الجديد"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/db.json"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            file_data = res.json()
            sha = file_data["sha"]
            content_decoded = base64.b64decode(file_data["content"]).decode("utf-8")
            db_json = json.loads(content_decoded)
        else:
            sha = None
            db_json = {}

        # إضافة البيانات والرابط الجديد
        db_json[slug] = new_entry

        updated_content = json.dumps(db_json, ensure_ascii=False, indent=2)
        encoded_content = base64.b64encode(updated_content.encode("utf-8")).decode("utf-8")

        payload = {
            "message": f"Update db.json for {slug} via Bot",
            "content": encoded_content,
        }
        if sha:
            payload["sha"] = sha

        requests.put(url, headers=headers, json=payload)
    except Exception as e:
        print(f"Error updating github: {e}")


# ====================================================
# 3. خطوات إنشاء وتحديث البيانات عبر البوت
# ====================================================
async def start_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("1️⃣ أرسل اسم الشخص (لمن):")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['name'] = update.message.text.strip()
    await update.message.reply_text("2️⃣ أرسل كود/اسم الرابط (Slug):")
    return SLUG

async def get_slug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['slug'] = update.message.text.strip()
    await update.message.reply_text("3️⃣ أرسل كلمة السر (الباسورد):")
    return PASSWORD

async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("4️⃣ أرسل الرسالة:")
    return MESSAGE_TEXT

async def get_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['message'] = update.message.text.strip()
    await update.message.reply_text("5️⃣
