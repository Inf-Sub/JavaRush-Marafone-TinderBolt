from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram import BotCommand, MenuButtonCommands, BotCommandScopeChat, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes


# конвертирует объект user в строку
def dialog_user_info_to_str(user) -> str:
    result = ""
    dialog_map = {
        "name": "Имя",
        "sex": "Пол",
        "age": "Возраст",
        "city": "Город",
        "occupation": "Профессия",
        "hobby": "Хобби",
        "goals": "Цели знакомства",
        "handsome": "Красота, привлекательность в баллах (максимум 10 баллов)",
        "wealth": "Доход, богатство",
        "annoys": "В людях раздражает"
    }
    for key, name in dialog_map.items():
        if key in user:
            result += name + ": " + user[key] + "\n"
    return result


# посылает в чат текстовое сообщение
async def send_text(
        update: Update, context: ContextTypes.DEFAULT_TYPE, text: str, parse_mode=ParseMode.MARKDOWN) -> Message:
    text = text.encode('utf16', errors='surrogatepass').decode('utf16')
    return await context.bot.send_message(
        chat_id=update.effective_chat.id, text=text, parse_mode=parse_mode)


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
    with open('resources/images/' + name + ".jpg", 'rb') as photo:
        return await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo)


# отображает команду и главное меню
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, commands: dict):
    command_list = [BotCommand(key, value) for key, value in commands.items()]
    await context.bot.set_my_commands(
        commands=command_list, language_code="en", scope=BotCommandScopeChat(chat_id=update.effective_chat.id))
    await context.bot.set_chat_menu_button(menu_button=MenuButtonCommands(), chat_id=update.effective_chat.id)


# загружает сообщение из папки  /resources/messages/
def load_message(name):
    with open("resources/messages/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


# загружает промпт из папки  /resources/messages/
def load_prompt(name):
    with open("resources/prompts/" + name + ".txt", "r", encoding="utf8") as file:
        return file.read()


class Dialog:
    pass
