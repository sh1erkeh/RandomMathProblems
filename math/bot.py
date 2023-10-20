from generator import generate
from math import ceil
from PIL import Image

import telebot
from telebot import types

TOKEN = "6429508312:AAFDUcFPPbw8pF7uGbRmVNMPZDeGgQGuCjg"
welcome_text = """"""

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_task = types.KeyboardButton(text="Задача")
    keyboard.add(button_task)
    bot.send_message(message.chat.id, text='Чтобы получить задачу, нажмите на кнопку "Задача" или введите "задача" в любом регистре.', reply_markup=keyboard)

@bot.message_handler(content_types=['text'])
def send_pic(message):
    if message.text.lower() == 'задача':
        generate()
        img = open('task.png', 'rb')
        try:
            bot.send_photo(message.chat.id, img)
        except telebot.apihelper.ApiTelegramException:
            w, h = img.size
            newH = ceil(w / 20)
            padded = Image.new('RGB', (w, newH), 'white')
            padded.paste(img, (0, int((newH - h) / 2)))
            padded.save('task.png')

            img = open('task.png', 'rb')
            bot.send_photo(message.chat.id, img)
        finally:
            pass

if __name__ == "__main__":
    bot.infinity_polling()