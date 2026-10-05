import base64
import json
import requests
import telebot
from telebot import types

TOKEN = '8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU'
ADMIN_CHAT_ID = '8718173410'

GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'  # حط توكن جيت هاب هنا
REPO_OWNER = 'mohamed-egypt7'
REPO_NAME = 'For-you-'
FILE_PATH = 'db.json'

bot = telebot.TeleBot(TOKEN)

# قاموس مؤقت لحفظ خطوات الإدخال لكل مستخدم
user_steps = {}
temp_data = {}


def get_db():
  url = (
      f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
  )
  headers = {'Authorization': f'token {GITHUB_TOKEN}'}
  r = requests.get(url, headers=headers)
  if r.status_code == 200:
    info = r.json()
    content = requests.get(info['download_url']).text
    return json.loads(content), info['sha']
  return {}, None


def update_db(data, sha, msg):
  url = (
      f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
  )
  headers = {'Authorization': f'token {GITHUB_TOKEN}'}
  encoded = base64.b64encode(
      json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
  ).decode('utf-8')
  payload = {'message': msg, 'content': encoded, 'sha': sha}
  r = requests.put(url, headers=headers, json=payload)
  return r.status_code in [200, 201]


@bot.message_handler(commands=['start'])
def start_command(message):
  if str(message.chat.id) != str(ADMIN_CHAT_ID):
    bot.reply_to(message, 'عذراً، هذا البوت مخصص للمالك فقط.')
    return

  markup = types.InlineKeyboardMarkup()
  btn_add = types.InlineKeyboardButton(
      '➕ إضافة مستخدم جديد', callback_data='btn_add'
  )
  markup.add(btn_add)

  bot.send_message(
      message.chat.id,
      'أهلاً بك يا محمد! 🚀 بوت الإدارة السلس جاهز للعمل.\nاضغط على الزر أدناه'
      ' للبدء:',
      reply_markup=markup,
  )


@bot.callback_query_handler(func=lambda call: call.data == 'btn_add')
def callback_add(call):
  chat_id = call.message.chat.id
  user_steps[chat_id] = 'waiting_for_name'
  temp_data[chat_id] = {}
  bot.answer_callback_query(call.id)
  bot.send_message(
      chat_id, '👤 أرسل الآن **اسم المستخدم** (Key):', parse_mode='Markdown'
  )


@bot.message_handler(
    func=lambda m: str(m.chat.id) == str(ADMIN_CHAT_ID)
    and m.chat.id in user_steps
)
def handle_steps(message):
  chat_id = message.chat.id
  step = user_steps.get(chat_id)
  text = message.text.strip()

  if step == 'waiting_for_name':
    temp_data[chat_id]['name'] = text
    user_steps[chat_id] = 'waiting_for_pass'
    bot.reply_to(
        message, '🔑 ممتاز! أرسل الآن **كلمة المرور**:', parse_mode='Markdown'
    )

  elif step == 'waiting_for_pass':
    temp_data[chat_id]['password'] = text
    user_steps[chat_id] = 'waiting_for_link'
    bot.reply_to(
        message,
        '🔗 رائع! أرسل الآن **الرابط** (أو اكتب `لا` لو مفيش):',
        parse_mode='Markdown',
    )

  elif step == 'waiting_for_link':
    link = '' if text.lower() == 'لا' else text
    temp_data[chat_id]['link'] = link

    name = temp_data[chat_id]['name']
    password = temp_data[chat_id]['password']

    # تنظيف الحالة
    del user_steps[chat_id]

    bot.reply_to(message, '⏳ جاري رفع البيانات وتحديث جيت هاب، ثواني...')

    db_data, sha = get_db()
    if not db_data:
      db_data = {}

    db_data[name] = {'password': password, 'link': link}

    success = update_db(db_data, sha, f'Add {name} via Button Bot')
    if success:
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              '➕ إضافة شخص آخر', callback_data='btn_add'
          )
      )
      link_display = link if link else 'لا يوجد'
      msg_text = (
          f'✅ تمت الإضافة بنجاح!\n'
          f'👤 الاسم: {name}\n'
          f'🔑 الباسورد: {password}\n'
          f'🔗 الرابط: {link_display}'
      )
      bot.send_message(chat_id, msg_text, reply_markup=markup)
    else:
      bot.send_message(
          chat_id, '❌ فشل التحديث على جيت هاب، تأكد من صحة التوكن.'
      )


if __name__ == '__main__':
  print('Bot with buttons is running...')
  bot.infinity_polling()
