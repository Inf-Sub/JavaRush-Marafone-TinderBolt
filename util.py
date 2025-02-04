import asyncio

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import BotCommand, MenuButtonCommands, BotCommandScopeChat, MenuButtonDefault, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.error import TimedOut
from tenacity import retry, stop_after_attempt, wait_fixed


# конвертирует объект user в строку
def dialog_user_info_to_str(user) -> str:
    result = ''
    dialog_map = {
        'name': 'Имя',
        'sex': 'Пол',
        'age': 'Возраст',
        'city': 'Город',
        'occupation': 'Профессия',
        'hobby': 'Хобби',
        'goals': 'Цели знакомства',
        'handsome': 'Красота, привлекательность в баллах (максимум 10 баллов)',
        'wealth': 'Доход, богатство',
        'annoys': 'В людях раздражает'
    }
    for key, name in dialog_map.items():
        if key in user:
            result += f'{name}: {user[key]}\n'
    return result

# Декоратор tenacity для повторных попыток
@retry(
    stop=stop_after_attempt(5), wait=wait_fixed(10),
    retry_error_callback=lambda retry_state: print("Error: send_text: Превышено максимальное количество попыток")
)
async def send_text(
        update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, parse_mode=ParseMode.MARKDOWN) -> Message:
    try:
        # Кодировка текста
        text = text.encode('utf16', errors='surrogatepass').decode('utf16')
        
        # Попытка отправки сообщения
        return await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)
    except TimedOut:
        print("Error: Попытка отправки сообщения превысила лимит времени")
        raise  # Поднимите исключение, чтобы tenacity обработал его и выполнил повторную попытку

# # посылает в чат текстовое сообщение
# async def send_text(
#         update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, parse_mode=ParseMode.MARKDOWN) -> Message:
#     text = text.encode('utf16', errors='surrogatepass').decode('utf16')
#     max_retries = 3  # Максимальное количество повторных попыток
#     retry_delay = 5  # Задержка перед повторной попыткой в секундах
#
#     for attempt in range(max_retries):
#         try:
#             return await context.bot.send_message(
#                 chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)
#         except TimedOut:
#             print(f"Попытка {attempt + 1} отправки сообщения превысила лимит времени")
#             if attempt < max_retries - 1:
#                 await asyncio.sleep(retry_delay)
#             else:
#                 print("Превышено максимальное количество попыток")
#                 raise  # Или выполните другие действия, если все попытки не удались

# #  OLD Version: посылает в чат текстовое сообщение
# async def send_text(
#         update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, parse_mode=ParseMode.MARKDOWN) -> Message:
#     text = text.encode('utf16', errors='surrogatepass').decode('utf16')
#     return await context.bot.send_message(
#         chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)

# # посылает в чат текстовое сообщение (обновлено)
# async def send_text(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
#     if text.count('_') % 2 != 0:
#         message = f"Строка '{text}' является невалидной с точки зрения markdown. Воспользуйтесь методом send_html()"
#         print(message)
#         return await update.message.reply_text(message)
#
#     text = text.encode('utf16', errors='surrogatepass').decode('utf16')
#     return await context.bot.send_message(
#         chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.MARKDOWN)


# посылает в чат html сообщение
async def send_html(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=ParseMode.HTML)


# посылает в чат текстовое сообщение, и добавляет к нему кнопки
async def send_text_buttons(
        update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, buttons: dict) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    keyboard = []
    for key, value in buttons.items():
        button = InlineKeyboardButton(str(value), callback_data=str(key))
        keyboard.append([button])

    reply_markup = InlineKeyboardMarkup(keyboard)
    return await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)


# посылает в чат фото
async def send_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> Message:
    with open(f'resources/images/{name}.jpg', 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


# отображает команду и главное меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(
        commands=command_list, scope=BotCommandScopeChat(chat_id=update.effective_chat.id)
    )
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


# Удаляем команды для конкретного чата
async def hide_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.delete_my_commands(scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonDefault(), chat_id=update.effective_chat.id)


# загружает сообщение из папки  /resources/messages/
def load_message(name):
    with open(f'resources/messages/{name}.txt', 'r', encoding="utf8") as file:
        return file.read()


# загружает промпт из папки  /resources/messages/
def load_prompt(name):
    with open(f'resources/prompts/{name}.txt', 'r', encoding='utf8') as file:
        return file.read()


# посылает в чат
async def get_bot_username(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.bot.username


async def delete_message(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        message: Message,
        delay: float = 0) -> None:
    """
    Удаляет сообщение с опциональной задержкой.

    :param update: Объект Update, содержащий информацию о запросе.
    :param context: Контекст, предоставляющий доступ к боту.
    :param message: Объект Message, представляющий сообщение, которое нужно удалить.
    :param delay: Время задержки перед удалением сообщения в секундах.
    """
    if delay > 0:
        await asyncio.sleep(delay)
    await context.bot.delete_message(chat_id=update.effective_chat.id, message_id=message.message_id)


class Dialog:
    pass
