from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio

from gpt import *
from util import *


async def sleep(*, sec: float = 0.5) -> None:
    await asyncio.sleep(sec)


async def paragraph() -> None:
    print(f"\n\n")


async def start(update, context) -> None:
    mode = "main"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)

    print(f"Incoming message: {question}")
    print(f"Sending message: {answer}")

    await show_main_menu(
        update=update, context=context, commands={
            "start": "главное меню бота",
            "profile": "генерация Tinder-профиля 😎",
            "opener": "сообщение для знакомства 🥰",
            "message": "переписка от вашего имени 😈",
            "date": "переписка со звездами 🔥",
            "gpt": "задать вопрос чату GPT 🧠",
        }
    )
    print(f"Update BOT menu")
    await paragraph()


async def gpt(update, context) -> None:
    mode = "gpt"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)
    print(f"Incoming message: {question}")
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Sending message: {answer}")
    await paragraph()


async def gpt_dialog(update, context) -> None:
    question = update.message.text
    print(f"Incoming message (question to ChatGPT): {question}")
    prompt = load_prompt(dialog.mode)
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=question)
    await send_text(update=update, context=context, text=f"*{answer}*")
    print(f"Sending message (answer at ChatGPT): {answer}")
    await paragraph()


async def date(update, context) -> None:
    mode = "date"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    # await send_text(update=update, context=context, text=answer)
    await send_text_buttons(
        update=update, context=context, text=answer, buttons={
            "date_grande": "Ариана Гранде",
            "date_robbie": "Марго Робби",
            "date_zendaya": "Зендея",
            "date_gosling": "Райан Гослинг",
            "date_hardy": "Том Харди",
        }
    )
    print(f"Incoming message: {question}")
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Sending message: {answer}")
    await paragraph()


async def date_dialog(update, context) -> None:
    pass


async def date_button(update, context) -> None:
    # sex = {"man": {"gosling", "hardy"}, "woman": {"grande", "robbie", "zendaya"}}
    sex = {"grande": "woman", "robbie": "woman", "zendaya": "woman", "gosling": "man", "hardy": "man"}
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_photo(update=update, context=context, name=query)
    await send_text(
        # update=update, context=context, text=f"Pressed button ID: {query}", parse_mode=ParseMode.HTML
        # update=update, context=context, text=f"Pressed button ID: `{query}`"
        # update=update, context=context,
        # text=f"Отличный выбор!\n
        # Пригласите {'парня' if (query[5:] in sex['man']) else 'девушку'} на свидание, за 5 сообщений"

        update=update, context=context,
        text=f"Отличный выбор!\n"
             f"Пригласите {'девушку' if ( sex[query[5:]] == 'woman') else 'парня'} на свидание, за 5 сообщений"
    )
    print(f"Pressed button ID: {query}")
    await paragraph()


async def hello(update, context) -> None:
    question = update.message.text
    print(f"Dialog Mode: {dialog.mode}")

    if dialog.mode == "gpt":
        await gpt_dialog(update=update, context=context)
    else:
        await send_text(update=update, context=context, text="*Привет!*")
        await sleep()
        await send_text(update=update, context=context, text="Как дела?!")
        await sleep()
        await send_text(update=update, context=context, text=f"Вы написали: {question}")
        await sleep()
        await send_photo(update=update, context=context, name="avatar_main")
        await sleep()
        await send_text_buttons(
            update=update, context=context, text="Запустить процесс?", buttons={
                "prc_start": " Запустить ",
                "prc_stop": " Остановить "
            }
        )
        print(f"Incoming message: {question}")
        await paragraph()


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(
        update=update, context=context, text=f"Процесс {'запущен' if 'start' in query != -1 else 'остановлен'}")
    print(f"Pressed button ID: {query}")
    await paragraph()


dialog = Dialog()
dialog.mode = None


chatgpt = ChatGptService(token=config_env['OPEN_AI_TOKEN'])


app = ApplicationBuilder().token(config_env['TELEGRAM_BOT_TOKEN']).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(hello_button))

app.run_polling()

