import telebot
import logging

from config import LOGS, COUNT_LAST_MSG, BLACK_LIST

from yandex_gpt import ask_gpt, speech_to_text, text_to_speech

from validators import check_number_of_users, is_gpt_token_limit, is_stt_block_limit, is_tts_symbol_limit

from os import getenv
from dotenv import load_dotenv

from database import create_database, add_message, select_n_last_messages

# настраиваем запись логов в файл
logging.basicConfig(filename=LOGS, level=logging.ERROR, format="%(asctime)s FILE: %(filename)s IN: %(funcName)s MESSAGE: %(message)s", filemode="w")

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# обрабатываем команду /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in BLACK_LIST:
        bot.send_message(message.chat.id, "Вы не совсем нравитесь моему разработчику,поэтому лучше вам больше не обращаться ко мне,и к нему тоже:)")
    else:
        bot.send_message(message.chat.id, "Привет! Отправь мне голосовое сообщение или текст, и я тебе отвечу!")
    create_database()

# обрабатываем команду /help
@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, "Чтобы приступить к общению, отправь мне голосовое сообщение или текст")
    create_database()

# обрабатываем команду /debug - отправляем файл с логами
@bot.message_handler(commands=['debug'])
def debug(message):
    with open("logs.txt", "rb") as f:
        bot.send_document(message.chat.id, f)

...


# обрабатываем голосовые сообщения
# Декоратор для обработки голосовых сообщений, полученных ботом
@bot.message_handler(content_types=['voice'])
def handle_voice(message: telebot.types.Message):
    try:
        # Проверка на максимальное количество пользователей
        status_check_users, error_message = check_number_of_users(message.from_user.id)
        if not status_check_users:
            # Если количество пользователей превышает максимально допустимое,
            # отправляем сообщение с ошибкой пользователю и прекращаем выполнение функции
            bot.send_message(message.from_user.id, error_message)
            return

    # Проверка на доступность аудиоблоков


        stt_blocks, error_message = is_stt_block_limit(message.from_user.id, message.voice.duration)
        if error_message:
            bot.send_message(message.from_user.id, error_message)
            return



        # Получение информации о голосовом файле и его загрузка
        file_id = message.voice.file_id  # Идентификатор голосового файла в сообщении
        file_info = bot.get_file(file_id)  # Получение информации о файле для загрузки
        file = bot.download_file(file_info.file_path)  # Загрузка файла по указанному пути

        # Преобразование голосового сообщения в текст с помощью SpeechKit
        status_stt, stt_text = speech_to_text(file)  # Обращение к функции speech_to_text для получения текста
        if not status_stt:
            # Отправка сообщения об ошибке, если преобразование не удалось
            bot.send_message(message.from_user.id, stt_text)
            return

        add_message(user_id=message.from_user.id, full_message=[stt_text, 'user', 0, 0, stt_blocks])


# Проверка на доступность GPT-токенов
        last_messages, total_spent_tokens = select_n_last_messages(message.from_user.id, COUNT_LAST_MSG)
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            bot.send_message(message.from_user.id, error_message)
            return
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)  # Обращение к GPT с запросом
        if not status_gpt:
            # Отправка сообщения об ошибке, если GPT не смог сгенерировать ответ
            bot.send_message(message.from_user.id, answer_gpt)
            return
        total_gpt_tokens += tokens_in_answer


        # Проверка на лимит символов для SpeechKit
        tts_symbols, error_message = is_tts_symbol_limit(message.from_user.id, answer_gpt)


        # Запись ответа GPT в БД
        add_message(user_id=message.from_user.id, full_message=[answer_gpt, 'assistant', total_gpt_tokens, tts_symbols, 0])


        if error_message:
            bot.send_message(message.from_user.id, error_message)
            return


        status_tts, voice_response = text_to_speech(answer_gpt)  # Обращение к функции text_to_speech для получения аудио
        if status_tts:
            bot.send_voice(message.from_user.id, voice_response, reply_to_message_id=message.id)
        else:
            bot.send_message(message.from_user.id, answer_gpt, reply_to_message_id=message.id)

    except Exception as e:
        logging.error(e)
        bot.send_message(message.from_user.id, "Не получилось ответить. Попробуй записать другое сообщение")




# обрабатываем текстовые сообщения
@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # ВАЛИДАЦИЯ: проверяем, есть ли место для ещё одного пользователя (если пользователь новый)
        status_check_users, error_message = check_number_of_users(message.from_user.id)
        if not status_check_users:
            bot.send_message(message.from_user.id, error_message)  # мест нет =(
            return

        # БД: добавляем сообщение пользователя и его роль в базу данных
        full_user_message = [message.text, 'user', 0, 0, 0]
        add_message(user_id=message.from_user.id, full_message=full_user_message)

        # ВАЛИДАЦИЯ: считаем количество доступных пользователю GPT-токенов
        # получаем последние 4 (COUNT_LAST_MSG) сообщения и количество уже потраченных токенов
        last_messages, total_spent_tokens = select_n_last_messages(message.from_user.id, COUNT_LAST_MSG)
        # получаем сумму уже потраченных токенов + токенов в новом сообщении и оставшиеся лимиты пользователя
        total_gpt_tokens, error_message = is_gpt_token_limit(last_messages, total_spent_tokens)
        if error_message:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(message.from_user.id, error_message)
            return

        # GPT: отправляем запрос к GPT
        status_gpt, answer_gpt, tokens_in_answer = ask_gpt(last_messages)
        # GPT: обрабатываем ответ от GPT
        if not status_gpt:
            # если что-то пошло не так — уведомляем пользователя и прекращаем выполнение функции
            bot.send_message(message.from_user.id, answer_gpt)
            return
        # сумма всех потраченных токенов + токены в ответе GPT
        total_gpt_tokens += tokens_in_answer

        # БД: добавляем ответ GPT и потраченные токены в базу данных
        full_gpt_message = [answer_gpt, 'assistant', total_gpt_tokens, 0, 0]
        add_message(user_id=message.from_user.id, full_message=full_gpt_message)

        bot.send_message(message.from_user.id, answer_gpt, reply_to_message_id=message.id)  # отвечаем пользователю текстом
    except Exception as e:
        logging.error(e)  # если ошибка — записываем её в логи
        bot.send_message(message.chat.id, "Не получилось ответить. Попробуй написать другое сообщение")

# обрабатываем все остальные типы сообщений

@bot.message_handler(func=lambda: True)
def handler(message):
    bot.send_message(message.chat.id, "Отправь мне голосовое или текстовое сообщение, и я тебе отвечу")




while True:
    try:
        bot.polling()
    except Exception as ex:
        pass