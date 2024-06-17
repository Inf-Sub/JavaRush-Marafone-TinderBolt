from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio

from config import env as config_env
from gpt import *
from util import *


# тут будем писать наш код :)


async def hello(update, context):
    await send_text(update, context, "*Привет!*")
    await asyncio.sleep(.5)
    await send_text(update, context, "Как дела?!")
    await asyncio.sleep(.5)
    await send_text(update, context, f"Вы написали: {update.message.text}")
    print(f"Incoming message: {update.message.text}")

    await send_photo(update, context, "avatar_main")
    await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
        "btn_start": " Старт ",  # Текст и команда кнопки "Старт"
        "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
    })


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки

    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(update, context, f"Процесс {'запущен' if query == 'btn_start' else 'остановлен'}")
    print(f"Pressed button: {query}")


async def start(update, context):
    await send_photo(update, context, "main")
    print(f"Incoming message: {update.message.text}")


app = ApplicationBuilder().token(config_env['TELEGRAM_BOT_TOKEN']).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, hello))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
