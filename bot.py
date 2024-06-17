from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *
from dotenv import dotenv_values

config_env = dotenv_values(".env")
# print(f"{config_env['TELEGRAM_TOKEN']}")
# тут будем писать наш код :)


async def hello(update, context):
    await send_text(update, context, "*Привет!*")
    await send_text(update, context, "Как дела?!")
    await send_text(update, context, f"Вы написали {update.message.text}")

    await send_photo(update, context, "avatar_main")
    await send_text_buttons(update, context, "Выберите режим работы", {  # Текст перед кнопкой
        "btn_start": " Старт ",  # Текст и команда кнопки "Старт"
        "btn_stop": " Стоп "  # Текст и команда кнопки "Стоп"
    })


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    print(f"{query} {type(query)} {len(query)}")
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(update, context, f"Процесс {'запущен' if query == 'btn_start' else 'остановлен'}")


async def start(update, context):
    await send_photo(update, context, "main")


app = ApplicationBuilder().token(config_env['TELEGRAM_TOKEN']).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, hello))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
