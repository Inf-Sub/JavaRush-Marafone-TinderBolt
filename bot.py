from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio

from gpt import *
from util import *


async def sleep(*, sec: float = 0.5) -> None:
    await asyncio.sleep(sec)


async def start(update, context) -> None:
    mode = "main"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update, context, mode)
    await send_text(update, context, answer)

    print(f"Incoming message: {question}")
    print(f"Sending message: {answer}")

    await show_main_menu(
        update, context, commands={
            "start": "главное меню бота",
            "profile": "генерация Tinder-профиля 😎",
            "opener": "сообщение для знакомства 🥰",
            "message": "переписка от вашего имени 😈",
            "date": "переписка со звездами 🔥",
            "gpt": "задать вопрос чату GPT 🧠",
        }
    )
    print(f"Update BOT menu")


async def gpt(update, context) -> None:
    mode = "gpt"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update, context, mode)
    await send_text(update, context, answer)
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Incoming message: {question}")
    print(f"Sending message: {answer}")


async def gpt_dialog(update, context) -> None:
    question = update.message.text
    print(f"Incoming message (question): {question}")
    prompt = load_prompt(dialog.mode)
    answer = await chatgpt.send_question(prompt, question)
    await send_text(update, context, f"*{answer}*")
    print(f"Sending message (answer GPT): {answer}")


async def hello(update, context) -> None:
    question = update.message.text
    print(f"Dialog Mode: {dialog.mode}")

    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    else:
        await send_text(update, context, "*Привет!*")
        await sleep()
        await send_text(update, context, "Как дела?!")
        await sleep()
        await send_text(update, context, f"Вы написали: {question}")
        await sleep()
        await send_photo(update, context, "avatar_main")
        await sleep()
        await send_text_buttons(
            update, context, "Запустить процесс?", {
                "prc_start": " Запустить ",
                "prc_stop": " Остановить "
            }
        )
        print(f"Incoming message: {question}")


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(update, context, f"Процесс {'запущен' if 'start' in query != -1 else 'остановлен'}")
    print(f"Pressed button ID: {query}")


dialog = Dialog()
dialog.mode = None


chatgpt = ChatGptService(token=config_env['OPEN_AI_TOKEN'])


app = ApplicationBuilder().token(config_env['TELEGRAM_BOT_TOKEN']).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(MessageHandler(filters.TEXT, hello))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
