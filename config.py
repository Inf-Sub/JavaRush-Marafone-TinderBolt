from os import environ, getenv
from json import loads as json_loads, dumps as json_dumps
from random import choice
from dotenv import load_dotenv


def get_config_env():
    # take environment variables from .env.
    load_dotenv()
    
    env = {
        'TELEGRAM_BOT_TOKEN': environ['TELEGRAM_BOT_TOKEN'],
        # 'OPEN_AI_TOKEN': os.environ['OPEN_AI_TOKEN'],
        'OPEN_AI_TOKEN': None,
        'OPEN_AI_TOKENS_JSON': environ['OPEN_AI_TOKENS'],
        'HTTP_PROXY': environ['HTTP_PROXY'],
        'QA_FOLDER': 'gpt_qa',
    }
    
    # Прочитать значение переменной окружения
    open_ai_tokens_json = env['OPEN_AI_TOKENS_JSON']
    
    # Декодировать JSON строку в словарь
    open_ai_tokens_dict = json_loads(open_ai_tokens_json)

    # # Фильтруем токены, имеющие статус True
    # valid_tokens = [value['TOKEN'] for key, value in open_ai_tokens_dict.items() if value['STATUS']]
    env['OPEN_AI_TOKENS'] = open_ai_tokens_dict
    
    # Если есть хотя бы один токен со статусом True, выбираем случайный из них
    # if valid_tokens:
    #     env['OPEN_AI_TOKEN'] = choice(valid_tokens)
        # print(f'Выбранный токен: {env['OPEN_AI_TOKEN']}')
    # else:
    #     print('Нет доступных токенов со статусом True')

    return env


def get_config_gpt():
    """
    Models:
    'babbage-002': Babbage-002
    - Это одна из моделей GPT-3, нацеленная на умеренные размеры задач. Хорошо сбалансирована для экономически
    эффективных приложений, требующих среднего уровня понимания естественного языка.
    
    'dall-e-2', 'dall-e-3': DALL-E 2 и DALL-E 3
    - Это модели, предназначенные для генерации изображений на основе текстовых описаний. DALL-E 2 был
    представлен раньше и работает с векторным представлением изображения, в то время как DALL-E 3 является
    улучшенной версией с более высоким разрешением и реалистичностью генерируемых изображений.
    
    'davinci-002': Davinci-002
    - Модель из серии GPT-3, предназначенная для обработки более сложных запросов и больших объемов данных.
    Davinci-002 обеспечивает более глубокое понимание и генерацию текста.
    
    'gpt-3.5-turbo': GPT-3.5 Turbo
    - Эта модель представляет собой улучшенную и более быструю версию GPT-3.5, оптимизированную для скорости и
    эффективности без значительной потери качества.
    
    'gpt-3.5-turbo-0125', 'gpt-3.5-turbo-1106', 'gpt-3.5-turbo-16k', 'gpt-3.5-turbo-instruct',
    'gpt-3.5-turbo-instruct-0914': GPT-3.5 Turbo (различные индексы)
    - Эти модификации GPT-3.5 Turbo (например, 0125, 1106, 16k) представляют собой различные конфигурации или
    версии, которые могут варьироваться по мощности, скорости или специфическому назначению.
    
    'gpt-4', 'gpt-4-0125-preview', 'gpt-4-0613', 'gpt-4-1106-preview': GPT-4 и его разновидности
    - GPT-4 — это болшой шаг вперед по сравнению с GPT-3 с улучшенными алгоритмами и большей мощностью обработки
    данных. Различные версии, такие как 0125-preview, 0613 и 1106-preview, отражают процесс разработки и
    тестирования с учетом различных параметров производительности.
    
    'gpt-4-turbo', 'gpt-4-turbo-2024-04-09', 'gpt-4-turbo-preview': GPT-4 Turbo
    - Это еще более усовершенствованная и оптимизированная версия GPT-4, направленная на максимизацию скорости
    и эффективности.
    
    'gpt-4o', 'gpt-4o-2024-05-13': GPT-4o
    - Эта серия обозначает возможно специализированную версию GPT-4, ориентированную на конкретные задачи
    оптимизации или применения.
    
    'text-embedding-3-large', 'text-embedding-3-small', 'text-embedding-ada-002': Text-Embedding Models
    - Модели такие как text-embedding-3-large и text-embedding-3-small предназначены для создания эмбеддингов
    текста, которые можно использовать для различных приложений, включая поиск по семантической близости и
    кластеризацию.
    
    'tts-1', 'tts-1-1106', 'tts-1-hd', 'tts-1-hd-1106': TTS (Text-to-Speech) Models
    - Модели tts-1, tts-1-1106 и tts-1-hd предназначены для преобразования текста в речь. Они варьируются от
    стандартного качества до высокого (HD), предоставляя более чистое и естественное звучание голоса.
    
    'whisper-1': Whisper-1
    - Это модель для распознавания речи, способная преобразовывать аудио в текст. Эффективна для различных
    языков и акцентов.
    """
    gpt = {
        'model': 'gpt-4o',
        # This model supports at most 4096 completion tokens
        'max_tokens': 4096,
        'temperature': 0.8,
        'timeout': 300.0,
    }
    # env = get_config_env()
    
    # Если есть хотя бы один токен со статусом True, выбираем случайный из них
    # if env['OPEN_AI_TOKENS']:
    #     gpt['OPEN_AI_TOKENS'] = env['OPEN_AI_TOKENS']
    #     # Фильтруем токены, имеющие статус True
    #     valid_tokens = [value['TOKEN'] for key, value in gpt['OPEN_AI_TOKENS'].items() if value['STATUS']]
    #     if valid_tokens:
    #         gpt['OPEN_AI_TOKEN'] = choice(valid_tokens)
    return gpt


if __name__ == '__main__':
    # print(
    #     f"env:\n{env['TELEGRAM_BOT_TOKEN']}\n\n"
    #     f"os.environ:\n{environ['TELEGRAM_BOT_TOKEN']}\n\n"
    #     f"os.getenv:\n{getenv('TELEGRAM_BOT_TOKEN')}\n\n"
    # )
    # print(f"os.environ:\n{environ}\n\n")

    # if valid_tokens:
    #     env['OPEN_AI_TOKEN'] = choice(valid_tokens)
    #     print(f'Выбранный токен: {env['OPEN_AI_TOKEN']}')
    # else:
    #     print('Нет доступных токенов со статусом True')
    print(get_config_env()['OPEN_AI_TOKEN'])
    config_env = get_config_env()
    print(config_env['OPEN_AI_TOKEN'])
