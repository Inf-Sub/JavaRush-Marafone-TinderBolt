from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio
import traceback

from gpt import *
from util import *


async def sleep(*, sec: float = 0.5) -> None:
    await asyncio.sleep(sec)


async def paragraph() -> None:
    print(f"Dialog Mode: {dialog.mode}")
    print(f"\n\n")


def say_func_name() -> str:
    stack = traceback.extract_stack()
    return stack[-2][2]


async def start(update, context) -> None:
    mode = "main"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)

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

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message: {question}")
    print(f"Sending message: {answer}")
    print(f"Update BOT menu")
    await paragraph()


async def gpt(update, context) -> None:
    mode = "gpt"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message: {question}")
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Sending message: {answer}")
    await paragraph()


async def gpt_dialog(update, context) -> None:
    question = update.message.text
    prompt = load_prompt(dialog.mode)
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=question)
    await send_text(update=update, context=context, text=f"*{answer}*")

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message (question to ChatGPT): {question}")
    print(f"Load Prompt (for ChatGPT): `{prompt}`")
    print(f"Sending message (answer at ChatGPT): {answer}")
    await paragraph()


async def date(update, context) -> None:
    mode = "date"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    # await send_text(update=update, context=context, text=answer)
    my_buttons = await send_text_buttons(
        update=update, context=context, text=answer, buttons={
            "date_grande": "Ариана Гранде",
            "date_robbie": "Марго Робби",
            "date_zendaya": "Зендея",
            "date_gosling": "Райан Гослинг",
            "date_hardy": "Том Харди",
        }
    )

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message: {question}")
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Sending message: {answer}")
    print(f"Sending buttons: {my_buttons}")
    await paragraph()


async def date_dialog(update, context) -> None:
    question = update.message.text
    my_message = await send_text(update=update, context=context, text=f"*ChatGPT набирает текст...*")
    answer = await chatgpt.add_message(question)
    # await send_text(update=update, context=context, text=f"*{answer}*")
    await my_message.edit_text(f"{answer}")

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message (question to ChatGPT in Dialog): {question}")
    print(f"Sending message (temp answer in Dialog): {my_message}")
    print(f"Sending message (answer at ChatGPT in Dialog): {answer}")


async def date_button(update, context) -> None:
    mode = "date"
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
    if dialog.mode != mode:
        print(f"ERROR: Dialog Mode: {dialog.mode}")
        dialog.mode = mode
        print(f"Changed Dialog Mode: {dialog.mode}")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)

    print(f"Function Name: {say_func_name()}")
    print(f"Pressed button ID: {query}")
    print(f"Load Prompt (for ChatGPT): `{prompt}`")
    await paragraph()


async def message(update, context) -> None:
    mode = "message"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(mode)
    await send_photo(update=update, context=context, name=mode)
    # await send_text(update=update, context=context, text=answer)
    my_buttons = await send_text_buttons(
        update=update, context=context, text=answer, buttons={
            "message_next": "Следующее сообщение",
            "message_date": "Пригласить на свидание",
        }
    )

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message: {question}")
    print(f"Changed Dialog Mode: {dialog.mode}")
    print(f"Sending message: {answer}")
    print(f"Sending buttons: {my_buttons}")
    await paragraph()

    dialog.list.clear()


async def message_dialog(update, context) -> None:
    question = update.message.text
    dialog.list.append(question)

    print(f"Function Name: {say_func_name()}")
    print(f"Incoming message (added Dialog List for ChatGPT): {question}")
    print(f"All messages in Dialog (All questions for ChatGPT in Dialog): {dialog.list}")
    # print(f"Sending message (answer at ChatGPT in Dialog): {answer}")
    await paragraph()


async def message_button(update, context) -> None:
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)
    prompt = load_prompt(query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update=update, context=context, text=f"*ChatGPT думает над вариантами ответа...*")
    answer = await chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(f"{answer}")

    print(f"Function Name: {say_func_name()}")
    print(f"Pressed button ID: {query}")
    print(f"Incoming messages in Dialog (All questions for ChatGPT in Dialog): {dialog.list}")
    print(f"Sending message (temp answer in Dialog): {my_message}")
    print(f"Sending message (answer at ChatGPT in Dialog): {answer}")
    await paragraph()


async def hello(update, context) -> None:
    question = update.message.text

    if dialog.mode is not None:
        await globals()[f"{dialog.mode}_dialog"](update=update, context=context)
    # if dialog.mode == "gpt":
    #     await gpt_dialog(update=update, context=context)
    # elif dialog.mode == "date":
    #     await date_dialog(update=update, context=context)
    # elif dialog.mode == "message":
    #     await message_dialog(update=update, context=context)
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

    print(f"Function Name: {say_func_name()}")
    print(f"Select Dialog Function: {dialog.mode}_dialog")
    print(f"Dialog Mode: {dialog.mode}")
    print(f"Incoming message: {question}")
    await paragraph()


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(
        update=update, context=context, text=f"Процесс {'запущен' if 'start' in query != -1 else 'остановлен'}")

    print(f"Function Name: {say_func_name()}")
    print(f"Pressed button ID: {query}")
    await paragraph()


dialog = Dialog()
dialog.mode = None
dialog.list = []


chatgpt = ChatGptService(token=config_env['OPEN_AI_TOKEN'])


app = ApplicationBuilder().token(config_env['TELEGRAM_BOT_TOKEN']).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(hello_button))

app.run_polling()

