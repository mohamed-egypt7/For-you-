import base64
import json
import os
import requests
import telebot

# بيانات البوت وشات آي دي الصحيحة الخاصة بك
TOKEN = '8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU'
ADMIN_CHAT_ID = '8718173410'

# بيانات جيت هاب (استبدل YOUR_GITHUB_TOKEN بتوكن جيت هاب الحقيقي الخاص بك)
GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'
REPO_OWNER = 'mohamed-egypt7'
REPO_NAME = 'For-you-'
FILE_PATH = 'db.json'

bot = telebot.TeleBot(TOKEN)


def get_db_from_github():
  url = (
      f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
  )
  headers = {'Authorization': f'token {GITHUB_TOKEN}'}
  r = requests.get(url, headers=headers)
  if r.status_code == 200:
    file_info = r.json()
    content = requests.get(file_info['download_url']).text
    return json.loads(content), file_info['sha']
  return {}, None


def update_db_on_github(data, sha, commit_message):
  url = (
      f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
  )
  headers = {'Authorization': f'token {GITHUB_TOKEN}'}
  content_encoded = base64.b64encode(
      json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
  ).decode('utf-8')
  payload = {'message': commit_message, 'content': content_encoded, 'sha': sha}
  r = requests.put(url, headers=headers, json=payload)
  return r.status_code in [200, 201]


@bot.message_handler(commands=['start'])
def send_welcome(message):
  if str(message.chat.id) != str(ADMIN_CHAT_ID):
    bot.reply_to(message, 'عذراً، هذا البوت مخصص للمالك فقط.')
    return
  bot.reply_to(
      message,
      'أهلاً بك يا محمد! 🚀 بوت الإدارة جاهز.\nلإضافة مستخدم جديد استخدم'
      ' الأمر:\n`/add الاسم كلمة_المرور الرابط`',
  )


@bot.message_handler(commands=['add'])
def add_item(message):
  if str(message.chat.id) != str(ADMIN_CHAT_ID):
    return
  try:
    parts = message.text.split(maxsplit=3)
    if len(parts) < 4:
      bot.reply_to(
          message,
          'خطأ في الصيغة! استخدم الأمر بهذا الشكل:\n`/add الاسم كلمة_المرور'
          ' الرابط`',
      )
      return

    _, name, password, link = parts

    db_data, sha = get_db_from_github()
    if sha is None and not db_data:
      db_data = {}

    db_data[name] = {'password': password, 'link': link}

    success = update_db_on_github(db_data, sha, f'Add {name} via Telegram Bot')
    if success:
      bot.reply_to(
          message,
          f'✅ تمت الإضافة ونشر البيانات بنجاح لـ: *{name}*',
          parse_mode='Markdown',
      )
    else:
      bot.reply_to(
          message,
          '❌ فشل التحديث على جيت هاب، تأكد من صلاحيات GitHub Token.',
      )
  except Exception as e:
    bot.reply_to(message, f'حدث خطأ: {e}')


if __name__ == '__main__':
  print('Bot is running 24/7...')
  bot.infinity_polling()
