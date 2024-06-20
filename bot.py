from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio
import traceback

from gpt import *
from util import *


async def sleep(*, sec: float = 0.5) -> None:
    await asyncio.sleep(sec)


async def paragraph() -> None:
    # print(f"{say_func_name()}\tDialog Mode: {dialog.mode}")
    print(f"{'=' * 20}")
    print(f"\n\n")


def say_func_name() -> str:
    stack = traceback.extract_stack()
    return f"Function Name: {stack[-2][2]}"


async def start(update, context) -> None:
    mode = "main"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(name=mode)
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

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    print(f"{say_func_name()}\tSending message:\t{answer}")
    print(f"{say_func_name()}\tUpdate BOT menu")
    await paragraph()


async def gpt(update, context) -> None:
    mode = "gpt"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(name=mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    print(f"{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}")
    print(f"{say_func_name()}\tSending message:\t{answer}")
    await paragraph()


async def gpt_dialog(update, context) -> None:
    question = update.message.text
    prompt = load_prompt(name=dialog.mode)
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=question)
    await send_text(update=update, context=context, text=f"*{answer}*")

    print(f"{say_func_name()}\tIncoming message (question to ChatGPT):\t{question}")
    print(f"{say_func_name()}\tLoad Prompt (for ChatGPT):\n`{prompt}`")
    print(f"{say_func_name()}\tSending message (answer at ChatGPT):\t{answer}")
    await paragraph()


async def date(update, context) -> None:
    mode = "date"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(name=mode)
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

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    print(f"{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}")
    print(f"{say_func_name()}\tSending message:\t{answer}")
    print(f"{say_func_name()}\tSending buttons:\t{my_buttons}")
    await paragraph()


async def date_dialog(update, context) -> None:
    question = update.message.text
    my_message = await send_text(update=update, context=context, text=f"*ChatGPT набирает текст...*")
    answer = await chatgpt.add_message(question)
    # await send_text(update=update, context=context, text=f"*{answer}*")
    await my_message.edit_text(f"{answer}")

    print(f"{say_func_name()}\tIncoming message (question to ChatGPT in Dialog):\t{question}")
    print(f"{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}")
    print(f"{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}")


async def date_button(update, context) -> None:
    mode = "date"
    # sex = {"man": {"gosling", "hardy"}, "woman": {"grande", "robbie", "zendaya"}}
    sex = {"grande": "woman", "robbie": "woman", "zendaya": "woman", "gosling": "man", "hardy": "man"}
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_photo(update=update, context=context, name=query)

    # Исправление ошибки при наличии в переменной {query} нижнего подчеркивания:
    # send_text(update, context, f"{query}" parse_mode=ParseMode.HTML) or send_text(update, context, f"`{query}`")
    await send_text(
        update=update, context=context,
        text=f"Отличный выбор!\n"
             f"Пригласите {'девушку' if ( sex[query[5:]] == 'woman') else 'парня'} на свидание, за 5 сообщений"
    )
    # alternate:
    # await send_text(
    #     update=update, context=context,
    #     text=f"Отличный выбор!\n
    #     Пригласите {'парня' if (query[5:] in sex['man']) else 'девушку'} на свидание, за 5 сообщений"
    # )

    if dialog.mode != mode:
        print(f"ERROR: Dialog Mode: {dialog.mode}")
        dialog.mode = mode
        print(f"Changed Dialog Mode: {dialog.mode}")

    prompt = load_prompt(name=query)
    chatgpt.set_prompt(prompt)

    print(f"{say_func_name()}\tPressed button ID:\t{query}")
    print(f"{say_func_name()}\tLoad Prompt (for ChatGPT):\n`{prompt}`")
    await paragraph()


async def message(update, context) -> None:
    mode = "message"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(name=mode)
    await send_photo(update=update, context=context, name=mode)
    # await send_text(update=update, context=context, text=answer)
    my_buttons = await send_text_buttons(
        update=update, context=context, text=answer, buttons={
            "message_next": "Следующее сообщение",
            "message_date": "Пригласить на свидание",
        }
    )

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    print(f"{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}")
    print(f"{say_func_name()}\tSending message:\t{answer}")
    print(f"{say_func_name()}\tSending buttons:\t{my_buttons}")
    await paragraph()

    dialog.list.clear()


async def message_dialog(update, context) -> None:
    question = update.message.text
    dialog.list.append(question)

    print(f"{say_func_name()}\tIncoming message (added Dialog List for ChatGPT):\t{question}")
    print(f"{say_func_name()}\tAll messages in Dialog (All questions for ChatGPT in Dialog):\t{dialog.list}")
    # print(f"{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}")
    await paragraph()


async def message_button(update, context) -> None:
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку

    prompt = load_prompt(name=query)
    chatgpt.set_prompt(prompt)
    # prompt = load_prompt(name=query)
    user_chat_history = "\n\n".join(dialog.list)
    my_message = await send_text(update=update, context=context, text=f"*ChatGPT думает над вариантами ответа...*")
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_chat_history)
    await my_message.edit_text(text=f"{answer}")

    print(f"{say_func_name()}\tPressed button ID:\t{query}")
    print(f"{say_func_name()}\tIncoming messages in Dialog (All questions for ChatGPT in Dialog):\t{dialog.list}")
    print(f"{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}")
    print(f"{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}")
    await paragraph()


async def profile(update, context) -> None:
    mode = "profile"
    dialog.mode = mode
    question = update.message.text
    answer = load_message(name=mode)
    await send_photo(update=update, context=context, name=mode)
    await send_text(update=update, context=context, text=answer)

    dialog.count = 0
    await send_text(update=update, context=context, text="Сколько Вам лет?")

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    print(f"{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}")
    print(f"{say_func_name()}\tSending message:\t{answer}")
    # print(f"{say_func_name()}\tSending buttons:\t{my_buttons}")
    await paragraph()


async def profile_dialog(update, context) -> None:
    mode = "profile"
    question = update.message.text
    dialog.count += 1

    print(
        f"{say_func_name()}\tDialog Count: {dialog.count}\tIncoming message (question to ChatGPT in Dialog): {question}"
    )

    if dialog.count == 1:
        dialog.user["age"] = question
        await send_text(update=update, context=context, text="Кем Вы работаете?")
    elif dialog.count == 2:
        dialog.user["occuration"] = question
        await send_text(update=update, context=context, text="У Вас есть хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = question
        await send_text(update=update, context=context, text="Что Вам НЕ нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = question
        await send_text(update=update, context=context, text="Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = question

        prompt = load_prompt(name=dialog.mode)
        user_info = dialog_user_info_to_str(user=dialog.user)

        my_message = await send_text(update=update, context=context, text=f"*ChatGPT обрабатывает Ваши данные...*")
        answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_info)
        await my_message.edit_text(text=f"{answer}")

        print(f"{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}")
        print(f"{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}")


async def hello(update, context) -> None:
    question = update.message.text

    print(f"{say_func_name()}\tDialog Mode:\t{dialog.mode}")

    if dialog.mode is not None and dialog.mode != "main":
        print(f"{say_func_name()}\tSelect Dialog Function:\t{dialog.mode}_dialog")
        await globals()[f"{dialog.mode}_dialog"](update=update, context=context)
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

    print(f"{say_func_name()}\tIncoming message:\t{question}")
    await paragraph()


async def hello_button(update, context):
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await send_text(
        update=update, context=context, text=f"Процесс {'запущен' if 'start' in query != -1 else 'остановлен'}")

    print(f"{say_func_name()}\tPressed button ID:\t{query}")
    await paragraph()


dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}


chatgpt = ChatGptService(token=config_env['OPEN_AI_TOKEN'])


app = ApplicationBuilder().token(token=config_env['TELEGRAM_BOT_TOKEN']).build()
app.add_handler(CommandHandler(command="start", callback=start))
app.add_handler(CommandHandler(command="gpt", callback=gpt))
app.add_handler(CommandHandler(command="date", callback=date))
app.add_handler(CommandHandler(command="message", callback=message))
app.add_handler(CommandHandler(command="profile", callback=profile))

app.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=hello))
app.add_handler(CallbackQueryHandler(callback=date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(callback=message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(callback=hello_button))

app.run_polling()

