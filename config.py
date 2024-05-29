

MAX_USERS = 4  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 120  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога
MAX_TTS_SYMBOLS = 220

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 120  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 50200  # 5 000 символов
MAX_USER_GPT_TOKENS = 20200  # 2 000 токенов

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник, и у тебя очень смешной юмор '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом
