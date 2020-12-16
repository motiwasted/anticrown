
import os
import telebot
import time
import datetime
import telebot_calendar
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
import psycopg2


DATABASE_URL = os.environ['DATABASE_URL']


con = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = con.cursor()

bot = telebot.TeleBot('1411404393:AAHbEKkWpU7NEfRdkt9mnhjSKJKektDXNAU')
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")

start_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
start_keyboard.row('Зарегистрировать мероприятие', 'Я заболел', 'Мои записи')
event_keyboard  = telebot.types.ReplyKeyboardMarkup(True,True)
event_keyboard.row('147685', '165034')
time_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
time_keyboard.row('Выбрать дату')
end_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
end_keyboard.row('/stopit')
save_button = telebot.types.ReplyKeyboardMarkup(True,True) 
save_button.row('Зарегистрировать посещение')
start_button = telebot.types.ReplyKeyboardMarkup(True,True)
start_button.row('/start')
photo_button = telebot.types.ReplyKeyboardMarkup(True,True)
photo_button.row('Зарегистрировать')
crown_button = telebot.types.ReplyKeyboardMarkup(True,True)
crown_button.row('Ближайшие точки')


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Пожалуйста зарегистрируете мероприятие или укажите свой актуальный статус, протекания болезни', reply_markup=start_keyboard)
    
def Set_up_event(message):
    mci = message.chat.id
    user_Task = message.text
    now = datetime.datetime.now()
    today = now.strftime('%d.%m.%Y')

    if user_Task == '147685':
        bot.send_message(message.chat.id, 'Зарегистрировано посещение в КАИ 5 корпус ' + user_Task , reply_markup= save_button)
    elif user_Task == '165034':
        bot.send_message(message.chat.id, 'Зарегистрировано посещение в КАИ 7 корпус ' + user_Task , reply_markup=save_button)
    elif message.content_type == 'photo':
        user_Task = '147685'
        bot.send_message(message.chat.id,'Зарегистрировано посещение в КАИ 5 корпус', reply_markup=photo_button)
    else:
        bot.send_message(message.chat.id, 'Некорректное сообщение ' + user_Task , reply_markup=event_keyboard)
    global sql_task 
    global sql_id
    global sql_date
    sql_date = today
    sql_id = mci
    sql_task = user_Task
    return sql_task,sql_date,sql_id

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'зарегистрировать мероприятие':
        mci = message.chat.id
        New_event = bot.send_message(mci,'Пожалуйста введите номер мероприятия или отправьте QR код')
        bot.register_next_step_handler(New_event , Set_up_event)
    elif message.text.lower() == 'мои записи':
        with con:
            mci = message.chat.id
            cursor.execute("SELECT * FROM crownmain WHERE user_id=%s",[mci])
            rows = cursor.fetchall()

            for row in rows:
                bot.send_message(message.chat.id,(f" айди компании  {row[1]}  дата  {row[2]}"), reply_markup=start_keyboard)
                
    elif message.text.lower() == 'зарегистрировать посещение':
        bot.send_message(message.chat.id, 'Данные сохранены', reply_markup=start_keyboard)
        cur = con.cursor()
        cur.execute (
        '''INSERT INTO crownmain (company_id,submite_date,user_id)
        VALUES (%s, %s, %s);
        ''',
        (sql_task,sql_date,sql_id))
        con.commit() 
    elif message.text.lower() == 'зарегистрировать':
        bot.send_message(message.chat.id, 'Данные сохранены', reply_markup=start_keyboard)
        cur = con.cursor()
        cur.execute (
        '''INSERT INTO crownmain (company_id,submite_date,user_id)
        VALUES (%s, %s, %s);
        ''',
        (sql_task,sql_date,sql_id))
        con.commit() 
    elif message.text.lower() == 'Я заболел':
        bot.send_message(435409717, 'Заболел человек, находящийся с вами в одном здании, пожалуйста сдайте тест', reply_markup=crown_button)
        
    else:
        bot.send_message(message.chat.id,'некорректное сообщение', reply_markup=start_button)


print("Bot was started \n " , time.strftime("%H:%M:%S", time.localtime()))
bot.polling()  