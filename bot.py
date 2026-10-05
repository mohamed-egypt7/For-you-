import base64
import json
import os
import requests
import telebot
from telebot import types

TOKEN = '8882621676:AAFNQ0B3q6rPSMTIujyIHGYiep9xNM1rgZU'
ADMIN_CHAT_ID = '8718173410'

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
    try:
      return json.loads(content), info['sha']
    except:
      return {}, info['sha']
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


def main_menu():
  markup = types.InlineKeyboardMarkup(row_width=1)
  btn_add = types.InlineKeyboardButton(
      '➕ إنشاء رسالة جديدة', callback_data='btn_add'
  )
  btn_list = types.InlineKeyboardButton(
      '📋 عرض كل الرسائل', callback_data='btn_list'
  )
  btn_del = types.InlineKeyboardButton(
      '🗑️ حذف رسالة', callback_data='btn_del_menu'
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
      'أهلاً بك يا محمد! 🚀 لوحة تحكم الرسائل جاهزة:',
      reply_markup=main_menu(),
  )


@bot.callback_query_handler(func=lambda call: call.data == 'btn_add')
def callback_add(call):
  chat_id = call.message.chat.id
  user_steps[chat_id] = 'waiting_for_name'
  temp_data[chat_id] = {}
  bot.answer_callback_query(call.id)
  bot.send_message(
      chat_id, '👤 اكتب **اسم الشخص** (رسالة إلى مين، مثل: محمد أو أحمد):'
  )


@bot.callback_query_handler(func=lambda call: call.data == 'btn_list')
def callback_list(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  db_data, _ = get_db()
  if not db_data:
    bot.send_message(chat_id, '📭 لا توجد أي رسائل مسجلة حالياً.')
    return

  text = '📋 قائمة الرسائل المسجلة:\n\n'
  for name, info in db_data.items():
    slug = info.get('slug', name)
    page_link = f'https://{REPO_OWNER}.github.io/{REPO_NAME}/index.html?to={slug}'
    text += (
        f'👤 الاسم: {name}\n🔗 الرابط: {page_link}\n------------------\n'
    )

  markup = types.InlineKeyboardMarkup()
  markup.add(
      types.InlineKeyboardButton('🔙 القائمة الرئيسية', callback_data='main_menu')
  )
  bot.send_message(chat_id, text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'btn_del_menu')
def callback_del_menu(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  db_data, _ = get_db()
  if not db_data:
    bot.send_message(chat_id, '📭 لا توجد رسائل للحذف.')
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
  bot.send_message(chat_id, '🗑️ اختر الرسالة التي تريد حذفها:', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('del_'))
def callback_execute_delete(call):
  chat_id = call.message.chat.id
  name_to_del = call.data.replace('del_', '', 1)
  bot.answer_callback_query(call.id)
  bot.send_message(chat_id, f'⏳ جاري حذف رسالة {name_to_del}...')
  db_data, sha = get_db()
  if name_to_del in db_data:
    del db_data[name_to_del]
    success = update_db(db_data, sha, f'Delete user {name_to_del}')
    if success:
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              '🔙 القائمة الرئيسية', callback_data='main_menu'
          )
      )
      bot.send_message(
          chat_id, f'✅ تم حذف رسالة {name_to_del} بنجاح!', reply_markup=markup
      )
    else:
      bot.send_message(chat_id, '❌ فشل التحديث على جيت هاب.')
  else:
    bot.send_message(chat_id, '⚠️ غير موجودة بالفعل.')


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def callback_main_menu(call):
  chat_id = call.message.chat.id
  bot.answer_callback_query(call.id)
  bot.send_message(chat_id, '🏠 القائمة الرئيسية:', reply_markup=main_menu())


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
    user_steps[chat_id] = 'waiting_for_slug'
    bot.reply_to(
        message,
        '🔗 أرسل الآن **اللينك الخاص** (مثال: `mohamed` أو `ggg` ليظهر في'
        ' الرابط):',
        parse_mode='Markdown',
    )

  elif step == 'waiting_for_slug':
    temp_data[chat_id]['slug'] = text
    user_steps[chat_id] = 'waiting_for_msg'
    bot.reply_to(
        message, '💬 أرسل الآن **نص الرسالة** التي ستظهر داخل صندوق الاقتباس:'
    )

  elif step == 'waiting_for_msg':
    temp_data[chat_id]['custom_message'] = text
    user_steps[chat_id] = 'waiting_for_song'
    bot.reply_to(
        message, '🎵 أرسل الآن **رابط الأغنية** (أو اكتب `لا` لو مفيش):'
    )

  elif step == 'waiting_for_song':
    song_link = '' if text.lower() in ['لا', 'no'] else text
    name = temp_data[chat_id]['name']
    slug = temp_data[chat_id]['slug']
    custom_msg = temp_data[chat_id]['custom_message']
    del user_steps[chat_id]

    bot.reply_to(message, '⏳ جاري الحفظ ورفع البيانات على جيت هاب...')

    db_data, sha = get_db()
    if not db_data:
      db_data = {}

    page_link = f'https://{REPO_OWNER}.github.io/{REPO_NAME}/index.html?to={slug}'

    db_data[slug] = {
        'name': name,
        'slug': slug,
        'message': custom_msg,
        'song_link': song_link,
        'link': page_link,
    }

    success = update_db(db_data, sha, f'Add message for {name}')
    if success:
      markup = types.InlineKeyboardMarkup()
      markup.add(
          types.InlineKeyboardButton(
              '🔙 القائمة الرئيسية', callback_data='main_menu'
          )
      )
      msg_text = (
          f'✅ تمت الإضافة بنجاح!\n\n👤 لمن: {name}\n🔗 الرابط:\n{page_link}\n💬'
          f' الرسالة: {custom_msg}\n🎵 الأغنية:'
          f' {song_link if song_link else "لا يوجد"}'
      )
      bot.send_message(chat_id, msg_text, reply_markup=markup)
    else:
      bot.send_message(chat_id, '❌ حدث خطأ أثناء التحديث على جيت هاب.')


if __name__ == '__main__':
  print('Bot is running successfully...')
  bot.infinity_polling()
