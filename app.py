import json
from easyocr import Reader
from io import BytesIO
from PIL import Image
import requests
import telebot
from telebot import types
from difflib import SequenceMatcher
import time
from itertools import islice
bot = telebot.TeleBot('6944064816:AAG6xP23JRAeUsYIarV0-p_XgLIBS7SjPO8')
bot.delete_webhook()
limit,flagdict,bladict,mesdict,tdict, ldict, flagdict2, timed, hdict = dict(),dict(),dict(),dict(),dict(),dict(),dict(),dict(),dict()

def namecheck(text:str, titl:list, q:int) -> bool:
  for j in titl:
    for i in range(8):
      if SequenceMatcher(None, text[i], j).ratio() > 0.34:
        return set(tdict[q][j].split())
  return ()

  
word1 = {'Вы подписались на канал'}
word2 = {'You joined this channel'}
flag = True

def checklink(x,q):
  global mesdict
  try:
    if 'https' in x:
      x = x.replace('https://t.me/','@')
    bot.get_chat_member_count(x)
  except:
    return False
  else:
    mesdict[q] = x
    return True

@bot.message_handler(content_types=["text", "audio", "document", "photo", "sticker", "video", "video_note", "voice", "location", "contact",
                 "new_chat_members", "left_chat_member", "new_chat_title", "new_chat_photo", "delete_chat_photo",
                 "group_chat_created", "supergroup_chat_created", "channel_chat_created", "migrate_to_chat_id",
                 "migrate_from_chat_id", "pinned_message", "animation"])
def get_text_messages(message):
  global flagdict, mesdict, tdict, bladict, ldict, limit, hdict, history
  markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
  itembtn = types.KeyboardButton('Правила')
  markup.add(itembtn)
  x = message.text
  y = message.id
  numb = message.chat.id
  name = message.from_user.first_name
  surname = message.from_user.last_name
  q = message.from_user.id
  if name == None: name = ''
  if surname == None: surname = ''
  flagdict[q] = True if q not in flagdict else flagdict[q]
  if q in timed and time.time() - timed[q] > 600: flagdict[q] = True
  if checklink(x,q) and flagdict[q]:
      if q not in limit:
        with open('hist.json') as l:
            history = json.load(l)
        with open('Mat.txt') as f:
          links = f.read().split()[::-1]
          links = sorted(set(links),key=links.index)
        if str(q) not in history: 
            ldict[q] = set(links[:3])
        else:
            ldict[q] = set(islice((i for i in links if i not in history[str(q)]),3))
        tdict[q] = {bot.get_chat(i).title:i for i in ldict[q]}
        linkstosub2 = ''.join('. '.join(str(i) for i in j) + '\n' for j in enumerate(ldict[q],start = 1))
        #bot.delete_message(chat_id=numb, message_id=y)
        hdict[q] = list(ldict[q])
        bot.send_message(numb, f"{name} {surname}, подпишитесь, пожалуйста, на каналы и пришлите скриншоты этих каналов за 10 минут.\n{linkstosub2}",reply_markup=markup)
        flagdict[q] = False
        mesdict[q] = message.text
        timed[q] = time.time()
      else:
        bot.delete_message(message.chat.id,message.message_id)
        bot.send_message(numb, f"{name} {surname}, ещё не прошли 3 чужие ссылки, дождитесь!",reply_markup=markup)
        
  elif flagdict[q] == False and (message.photo != None):
      try:
          file_id = message.photo[-1].file_id
          file_path = bot.get_file(file_id).file_path
          l = f"https://api.telegram.org/file/bot{bot.token}/{file_path}"
      except Exception as er:
        print(er)
        l = message.text
      imglink = requests.get(l,stream=True).content
      bot.delete_message(message.chat.id,message.message_id)
      img = Image.open(BytesIO(imglink))
      reader = Reader(["ru","en"], gpu = False, verbose = False)
      text = reader.readtext(img,detail = 0)
      settext = set(text)
      strtext = str(text).lower()
      bladict[q] = namecheck(text,tdict[q],q)
      print(bladict[q])
      if any(bladict[q]) and ((len(word2&settext) >= len(word2) - 1 or "MUTE" in strtext) or (len(word1&settext) >= len(word1) - 1) or 'откл' in strtext or 'убрать' in strtext):
        ldict[q] = set(ldict[q]) - bladict[q]
        tdict[q] = {i:g for i,g in tdict[q].items() if tdict[q][i] != ''.join(bladict[q])}
      if ldict[q] != set():
        linkstosub2 = ''.join('. '.join(str(i) for i in j) + '\n' for j in enumerate(ldict[q],start = 1))
        bot.send_message(numb, f"{name} {surname}, вы пропустили каналы.\n{linkstosub2}",reply_markup=markup)
      else:
        with open('Mat.txt','a') as f:
          if 'https' in mesdict[q]:
            mesdict[q] = mesdict[q].replace('https://t.me/','@')
          f.write(f' {mesdict[q]}')
        bot.send_message(-1002039773694, f"{name} {surname}, ссылка {mesdict[q]} добавлена!",reply_markup=markup)
        hdict[q].append(mesdict[q])
        print(hdict)
        with open('hist.json','w') as l:
            json.dump(hdict,l)
        del ldict[q], flagdict[q], mesdict[q], timed[q]
        limit[q] = 4
        limit={i:i2-1 for i,i2 in limit.items() if i2 != 1}
  elif checklink(x,q):
    bot.delete_message(message.chat.id,message.message_id)
    bot.send_message(-1002039773694, f"{name} {surname}, после ссылки нужно публиковать только скрины.",reply_markup=markup)
  elif message.text == "Правила":
    bot.delete_message(chat_id=-1002039773694, message_id=y)
    bot.send_message(-1002039773694, 'Вы в чате 🚀ВЗАИМНЫЕ ВСТУПЛЕНИЯ НА КАНАЛЫ 3|3🚀\n'
                          '\n'
                          'Здесь мы подписываемся на каналы друг друга.\n\n'
                          'Участие в ленте чата БЕСПЛАТНОЕ.\n'
                          '\n'
                          'Работаем 3 через 3 + отработка 𝓑𝓤𝞟.\n\n'
                          'Взамен мы просим, подписаться на обязательные каналы и каналы-𝓑𝓤𝞟.\n'
                          '\n'
                          'Чем больше подписчиков на вашем канале, тем больше интерес и активность пользователей.\nЭто помогает продвинуть ваш канал в ленте новостей и увеличить рейтинг \n'
                          '\n'
                          '👇🏻👇🏻👇\n'
                          '\n'
                          '❗️ПРАВИЛА❗️\n'
                          '\n'
                          'В чате работает БОТ и отвечает за все процессы\n'
                          '\n'
        '✅Разрешается публиковать только ссылку на канал и СКРИН канала, на который подписался\n'
        '\n'
        '✅Публиковать свою ссылку можно один раз через 3 чужие ссылки и далее подписываться на каждый канал из трёх, что будет выше вашей ссылки\n\n'
        '✅После подписки на канал прислать СКРИН этого канала в чат\n'
        '\n'
        '❗Запрещается размещать свою ссылку и выходить из канала,за отписки бан.\n'
        '\n'
        )
  else:
    if message.from_user.username != 'dianamayskaia':
        bot.delete_message(chat_id=-1002039773694, message_id=y)
        bot.send_message(-1002039773694, f"{name} {surname}, разрешается публиковать только ссылку на канал и скрин канала, на который подписался! Исправьтесь!",reply_markup=markup)
while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)