

MAX_USERS = 35  # максимальное кол-во пользователей
MAX_GPT_TOKENS = 170  # максимальное кол-во токенов в ответе GPT
COUNT_LAST_MSG = 4  # кол-во последних сообщений из диалога
MAX_TTS_SYMBOLS = 800
ADMINS = [911334605, 2003103018]
BLACK_LIST = [1264528479, 860018854, 6567945703, 1106035854, 1039423406, 1647761506, 518236259]

# лимиты для пользователя
MAX_USER_STT_BLOCKS = 25  # 10 аудиоблоков
MAX_USER_TTS_SYMBOLS = 5000  # 5 000 символов
MAX_USER_GPT_TOKENS = 5000  # 2 000 токенов

LOGS = 'logs.txt'  # файл для логов
DB_FILE = 'messages.db'  # файл для базы данных
SYSTEM_PROMPT = [{'role': 'system', 'text': 'Ты веселый собеседник, и у тебя очень смешной юмор '
                                            'Поддерживай диалог. Не объясняй пользователю, что ты умеешь и можешь. '
                                            'Изображай человека'}]  # список с системным промтом
