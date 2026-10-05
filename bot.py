import base64
import json
import os
import requests
import telebot
from telebot import types

TOKEN = '8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU'
ADMIN_CHAT_ID = '8718173410'

# قراءة التوكن محلياً بأمان تام
GITHUB_TOKEN = 'YOUR_GITHUB_TOKEN'
try:
  if os.path.exists('my_token.txt'):
    with open('my_token.txt', 'r', encoding='utf-8') as f:
      GITHUB_TOKEN = f.read().strip()
except Exception as e:
  print('❌ خطأ في قراءة ملف التوكن:', e)

REPO_OWNER = 'mohamed-egypt7'
REPO_NAME = 'For-you-'
FILE_PATH = 'db.json'

bot = telebot.TeleBot(TOKEN)

user_steps = {}
temp_data = {}


def get_db():
  url = (
      f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}'
  )
  headers = {
      'Authorization': f'Bearer {GITHUB_TOKEN}',
      'Accept': 'application/vnd.github+json',
  }
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
  headers = {
      'Authorization': f'Bearer {GITHUB_TOKEN}',
      'Accept': 'application/vnd.github+json',
  }
  encoded = base64.b64encode(
      json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8')
  ).decode('utf-8')
  payload = {'message': msg, 'content': encoded, 'sha': sha}
  r = requests.put(url, headers=headers, json=payload)
  return r.status_code in [200, 201]


# القائمة الرئيسية
def main_menu():
  markup = types.InlineKeyboardMarkup(row_width=1)
  btn_add = types.InlineKeyboardButton(
      '➕ إضافة مستخدم جديد', callback_data='btn_add'
  )
  btn_list = types.InlineKeyboardButton(
      '📋 عرض كل المستخدمين', callback_data='btn_list'
  )
  btn_del = types.InlineKeyboardButton(
      '🗑️ حذف مستخدم', callback_data='btn_del_menu'
  )
  markup.add(btn_add, btn_list, btn_del)
  return markup


@bot.message_handler(commands=['start'])
def start_command(message):
  if str(message.chat.id) != str(ADMIN_CHAT_ID):
    bot.reply_to(message, 'عذراً، هذا البوت مخصص للمالك فقط.')
    return

  bot.send_message(
      message.chat.id,
      'أهلاً بك يا محمد! 🚀 لوحة تحكم الموقع جاهزة.\nاختر ما تحب فعله:',
      reply_markup=main_menu(),
  )


# زر إضافة مستخدم
@bot.callback_query_handler(func=lambda call: call.data == 'btn_add')
def callback_add(call):
  chat_id = call.message.chat.id
  user_steps[chat_id] = 'waiting_for_name'
  temp_data[chat_id] = {}
  bot.answer_callback_query(call.id)
  bot.send_message(
      chat_id, '👤 أرسل الآن **اسم المستخدم** (Key):', parse_mode='Markdown'
  )


# زر عرض المستخدمين
@bot.callback_query_handler(func=lambda call: call.data == 'btn_list')
def callback_list(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  db_data, _ = get_db()
  if not db_data:
    bot.send_message(chat_id, '📭 قاعدة البيانات فارغة حالياً.')
    return

  text = '📋 **قائمة المستخدمين المسجلين:**\n\n'
  for name, info in db_data.items():
    pwd = info.get('password', '')
    lnk = info.get('link', 'لا يوجد')
    text += f'👤 **الاسم:** `{name}`\n🔑 **الباسورد:** `{pwd}`\n🔗 **الرابط:** {lnk}\n------------------\n'

  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton('🔙 القائمة الرئيسية', callback_data='main_menu')
  )
  bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=markup)


# زر قائمة الحذف
@bot.callback_query_handler(func=lambda call: call.data == 'btn_del_menu')
def callback_del_menu(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  db_data, _ = get_db()
  if not db_data:
    bot.send_message(chat_id, '📭 لا يوجد أي مستخدمين للحذف.')
    return

  markup = types.InlineKeyboardMarkup(row_width=1)
  for name in db_data.keys():
    markup.add(
        types.InlineKeyboardButton(
            f'❌ حذف: {name}', callback_data=f'del_{name}'
        )
    )
  markup.add(
      types.InlineKeyboardButton('🔙 القائمة الرئيسية', callback_data='main_menu')
  )
  bot.send_message(
      chat_id,
      '🗑️ اختر المستخدم الذي تريد حذفه وإزالته من الموقع:',
      reply_markup=markup,
  )


# تنفيذ الحذف الفعلي
@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def callback_execute_delete(call):
  chat_id = call.message.chat.id
  name_to_del = call.data.replace('del_', '', 1)
  bot.answer_callback_query(call.id)

  bot.send_message(chat_id, f'⏳ جاري حذف المستخدم `{name_to_del}` وتحديث جيت هاب...')

  db_data, sha = get_db()
  if name_to_del in db_data:
    del db_data[name_to_del]
    success = update_db(
        db_data, sha, f'Delete user {name_to_del} via Telegram Bot'
    )
    if success:
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              '🔙 القائمة الرئيسية', callback_data='main_menu'
          )
      )
      bot.send_message(
          chat_id,
          f'✅ تم حذف المستخدم **{name_to_del}** بنجاح وتحديث الموقع!',
          parse_mode='Markdown',
          reply_markup=markup,
      )
    else:
      bot.send_message(chat_id, '❌ فشل التحديث على جيت هاب.')
  else:
    bot.send_message(chat_id, '⚠️ المستخدم غير موجود بالفعل.')


# الرجوع للقائمة الرئيسية عبر الأزرار
@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def callback_main_menu(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  bot.send_message(
      chat_id, '🏠 القائمة الرئيسية:', reply_markup=main_menu()
  )


# خطوات إضافة المستخدم
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
              '🔙 القائمة الرئيسية', callback_data='main_menu'
          )
      )

      # عرض الرابط بشكل مباشر وقابل للضغط إن وُجد
      link_display = (
          f'[اضغط هنا لفتح الصفحة]({link})' if link.startswith('http') else link
      )
      if not link_display:
        link_display = 'لا يوجد'

      msg_text = (
          f'✅ تمت الإضافة بنجاح وتحديث الموقع!\n\n'
          f'👤 الاسم: `{name}`\n'
          f'🔑 الباسورد: `{password}`\n'
          f'🔗 الرابط: {link_display}'
      )
      bot.send_message(
          chat_id,
          msg_text,
          parse_mode='Markdown',
          reply_markup=markup,
          disable_web_page_preview=False,
      )
    else:
      bot.send_message(
          chat_id, '❌ فشل التحديث على جيت هاب، تأكد من صحة الصلاحيات.'
      )


if __name__ == '__main__':
  print('Bot with full control panel is running...')
  bot.infinity_polling()
