import os
import telebot
import time
import datetime
import telebot_calendar
from telebot_calendar import CallbackData
from telebot.types import ReplyKeyboardRemove, CallbackQuery
import psycopg2
import dj_database_url

DATABASE_URL = os.environ['DATABASE_URL']
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

con = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = con.cursor()

bot = telebot.TeleBot('1303412518:AAHBYrrX0Ne4NwSqbNOvQlZMcS5BkBNtPDE')
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")

start_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
start_keyboard.row('Новая цель!', 'Мои задачи')
time_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
time_keyboard.row('Выбрать дату')
end_keyboard = telebot.types.ReplyKeyboardMarkup(True,True)
end_keyboard.row('/stopit')
save_button = telebot.types.ReplyKeyboardMarkup(True,True)
save_button.row('ДА!')
start_button = telebot.types.ReplyKeyboardMarkup(True,True)
start_button.row('/start')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в будущее! Что я делаю? Всё очень просто: ТЫ ставишь цели,а Я про них тебе напоминаю. Начнём?', reply_markup=start_keyboard)
    

def Set_up_task(message):
    mci = message.chat.id
    user_Task = message.text
    bot.send_message(message.chat.id, 'Так-так посмотрим что там у нас:  ' + user_Task , reply_markup=time_keyboard)
    global sql_task 
    global sql_id
    sql_id = mci
    sql_task = user_Task
    return sql_task, sql_id

@bot.message_handler(commands=['stopit'])
def stop_it(message):
    bot.send_message(message.chat.id, 'bye', reply_markup=start_keyboard)
    bot.stop_bot()

@bot.message_handler(content_types=['text'])
def send_text(message):
    if message.text.lower() == 'новая цель!':
        mci = message.chat.id
        New_task = bot.send_message(mci, 'Нет ничего лучше, чем записывать новые цели! Разве что... ИХ ВЫПОЛНЯТЬ! Записывай: ')
        bot.register_next_step_handler(New_task , Set_up_task)
    elif message.text.lower() == 'пока':
        bot.send_message(message.chat.id, 'Надеюсь ты вернёшься скоро!')

    elif message.text.lower() == 'мои задачи':
        with con:
            mci = message.chat.id
            cursor.execute("SELECT * FROM tasks WHERE user_id=%s",[mci])

            rows = cursor.fetchall()

            for row in rows:
                bot.send_message(message.chat.id,(f"{row[1]} {row[2]} {row[3]}"), reply_markup=start_keyboard)
                
    elif message.text.lower() == 'да!':
        bot.send_message(message.chat.id, 'Отлично! вот и новая цель!', reply_markup=start_keyboard)
        cur = con.cursor()
        cur.execute (
        '''INSERT INTO tasks (user_id,goal,dline)
        VALUES (%s, %s, %s);
        ''',
        (sql_id,sql_task,sql_date))
        con.commit() 
    elif message.text.lower() =='выбрать дату':
        now = datetime.datetime.now()
        today = now.strftime('%d.%m.%Y')
        bot.send_message(
            message.chat.id,
            text = f"На какой день планируем?) \nCейчас: {today}",
            reply_markup=telebot_calendar.create_calendar(
                name=calendar_1.prefix,
                year=now.year,
                month=now.month,  
            ),
        )
        
    else:
        bot.send_message(message.chat.id,'Я бы мог отзывться на подобные сообщения, но удобнее же кнопки! Начнём сначала: ', reply_markup=start_button)

@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def callback_inline(call: CallbackQuery):
    
    name, action, year, month, day = call.data.split(calendar_1.sep)

    date = telebot_calendar.calendar_query_handler(
        bot=bot, call=call, name=name, action=action, year=year, month=month, day=day
    )
    if action == "DAY":
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Ты выбрал {date.strftime('%d.%m.%Y')}",
            reply_markup=ReplyKeyboardRemove(),

        )
        bot.send_message(
            chat_id=call.from_user.id,
            text=f"Твоя задача: {sql_task} Ты обещаешь её выполнить до {date.strftime('%d.%m.%Y')} \n  Всё верно?",
            reply_markup=save_button,
        )
        global sql_date
        sql_date = date.strftime('%d.%m.%Y')
        return sql_date
        print(f"{calendar_1}: Day: {date.strftime('%d.%m.%Y')}")
        
    elif action == "CANCEL":
        bot.send_message(
            chat_id=call.from_user.id,
            text="Cancellation",
            reply_markup=ReplyKeyboardRemove(),
        )
        print(f"{calendar_1}: Cancellation")


print("Bot was started \n " , time.strftime("%H:%M:%S", time.localtime()))
bot.polling()