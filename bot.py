import json
import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# التوكنات ومعرفات الآدمن
BOT_TOKEN = "8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU"
ADMIN_CHAT_ID = "8718173410"

# بيانات جيت هاب لرفع التحديثات أوتوماتيك (تأكد من وضع بياناتك الصحيحة هنا)
GITHUB_TOKEN = "YOUR_GITHUB_PERSONAL_ACCESS_TOKEN"  # توكن جيت هاب الخاص بك
REPO_OWNER = "YOUR_GITHUB_USERNAME"                # اسم حسابك على جيت هاب
REPO_NAME = "YOUR_REPO_NAME"                      # اسم المستودع (Repository)
FILE_PATH = "db.json"                             # مسار ملف الجي سون في المشروع

def update_github_json(visitor_id, admin_message):
    try:
        # جلب الملف الحالي من جيت هاب
        url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        r = requests.get(url, headers=headers)
        
        file_data = r.json()
        sha = file_data.get("sha")
        content = json.loads(requests.get(file_data["download_url"]).text) if r.status_code == 200 else {}
        
        # إضافة الرد الجديد الخاص بالزائر
        content[visitor_id] = admin_message
        
        # رفع الملف المحدث لـ جيت هاب
        import base64
        new_content = base64.b64encode(json.dumps(content, ensure_ascii=False, indent=4).encode('utf-8')).decode('utf-8')
        
        data = {
            "message": f"Update reply for visitor {visitor_id}",
            "content": new_content,
            "sha": sha
        }
        requests.put(url, headers=headers, json=data)
    except Exception as e:
        print(f"Error updating GitHub: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message:
        return

    # التأكد أن الرسالة من الآدمن ومعها Reply على رسالة سابقة
    if str(message.chat_id) == ADMIN_CHAT_ID and message.reply_to_message:
        original_text = message.reply_to_message.text
        admin_reply = message.text

        # استخراج معرف الزائر أو الـ IP من نص الرسالة الأصلية التي وصلت لك
        # (نفترض أن رسالة الزائر الأصلية كانت تحتوي على معرّف أو IP في السطر الأول)
        visitor_id = "default_user"
        for line in original_text.split('\n'):
            if "IP" in line or "ID" in line or "الزائر" in line:
                visitor_id = line.split(":")[-1].strip()
                break

        # تحديث ملف الـ JSON أوتوماتيك
        update_github_json(visitor_id, admin_reply)
        
        await message.reply_text(f"✅ تم إرسال الرد للزائر بنجاح:\n{admin_reply}")

async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("🤖 البوت يعمل الآن ويراقب الردود ويحدث GitHub...")
    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
