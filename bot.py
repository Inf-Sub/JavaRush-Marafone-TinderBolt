from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

import asyncio
import traceback
from random import choice

import gpt as ai
import util
import saver
import token_mgr

from config import get_config_env
from config import get_config_gpt


def say_func_name() -> str:
    # await sleep(0)  # Имитируем асинхронную операцию
    stack = traceback.extract_stack()
    return f"Function Name: {stack[-2][2]}"


def create_storage():
    stored_value = None

    async def store(value=None):
        nonlocal stored_value
        if value is not None:
            stored_value = value
        return stored_value

    return store


async def not_divisible_by_even(num):
    # Проверим, если число делится на 2
    return num % 2 != 0


async def count_triple_dashes(text, find):
    await aio_sleep(0)  # Имитируем асинхронную операцию
    return text.count(find)


async def count_triple_dashes_and_check(text, find):
    # Подсчитываем количество тройных дефисов
    count = await count_triple_dashes(text, find)
    # Проверяем, если это число не кратно четному числу
    return await not_divisible_by_even(count)


async def aio_sleep(sec: float = 0.5) -> None:
    await asyncio.sleep(sec)


async def paragraph() -> None:
    await aio_sleep(0)  # Имитируем асинхронную операцию
    # print(f"{say_func_name()}\tDialog Mode: {dialog.mode}")
    print(f"{'=' * 20}\n\n")


async def welcome_message_with_delayed_deletion(
        update, context, name=None, text=None, delay=0, delete_init=True) -> None:
    if name is not None:
        photo_message = await util.send_photo(update=update, context=context, name=name)
    if text is not None:
        text_message = await util.send_text(update=update, context=context, text=text)
        
    if delete_init:
        await util.delete_message(update=update, context=context, message=update.message, delay=delay)
        delay = 0

    if name is not None:
        await util.delete_message(update=update, context=context, message=photo_message, delay=delay)
        delay = 0

    if text is not None:
        await util.delete_message(update=update, context=context, message=text_message, delay=delay)
    

async def start(update, context) -> None:
    mode = "main"
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    delete_delay = 3
    
    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)

    await util.show_main_menu(
        update=update, context=context, commands={
            'start': 'главное меню бота',
            'profile': 'генерация Tinder-профиля 😎',
            'opener': 'сообщение для знакомства 🥰',
            'message': 'переписка от вашего имени 😈',
            'date': 'переписка со звездами 🔥',
            'gpt': 'задать вопрос чату GPT 🧠',
        }
    )

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tSending message:\t{answer}')
    print(f'{say_func_name()}\tUpdate BOT menu')
    await paragraph()


async def gpt(update, context) -> None:
    global chatgpt
    mode = 'gpt'
    dialog.mode = mode
    question = update.message.text
    template_answer = util.load_message(name=mode)
    delete_delay = 3

    # await file_saver.save_qa_pair(question, answer)

    prompt = util.load_prompt(name=f'{dialog.mode}_start')
    hide_question = (
        'На какой модели GPT ты основан? Ответь лаконично. "GPT-... Дата выпуска, дата данных и актуализации данных."'
    )

    while chatgpt is not None:
        # Выполняем запрос
        answer = await chatgpt.send_question(prompt_text=prompt, message_text=hide_question)
        
        # Проверяем ответ на наличие ошибок
        if 'Authentication Error' in answer or 'Rate Limit Error' in answer:
            # Инициализируем сервис заново
            chatgpt = initialize_chatgpt_service()
            # Отправляем пользователю уведомление об ошибке
            await util.send_text(update=update, context=context, text=f'{answer}')
        else:
            # Если ошибок нет, выходим из цикла
            break
    # Если chatgpt стал None, уведомляем пользователя о проблеме инициализации
    else:
        await util.send_text(
            update=update, context=context, text=f'Работа с ChatGPT не инициализирована! Нет рабочих токенов!')

    # Находим минимальный индекс среди запятой, точки и пробела
    comma_index = answer.find(',')
    dot_index = answer.find('.')
    space_index = answer.find(' ')

    # Определяем минимальный индекс
    min_index = min(i for i in [comma_index, dot_index, space_index] if i != -1)
    await storage_function(f'{answer[:min_index]}:\n\n')

    answer += f'\n\n{template_answer}'
    
    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    print(f'{say_func_name()}\tSending message:\t{answer}')

    await paragraph()


async def gpt_dialog(update, context) -> None:
    question = update.message.text
    prompt = util.load_prompt(name=dialog.mode)
    message_text_wait = '*ChatGPT думает над вариантами ответа...*'
    my_message = await util.send_text(update=update, context=context, text=message_text_wait)
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=question)
    # try:
    #     await my_message.edit_text(text=f'{answer}', parse_mode=util.ParseMode.MARKDOWN)
    # except Exception as e:
    #     await util.send_text(update=update, context=context, text=f'{answer}')
    #     await util.send_text(update=update, context=context, text=f'*ERROR:*\n\n{e}', parse_mode=util.ParseMode.MARKDOWN)

    # Получаем сохраненное значение
    answer = await storage_function() + answer

    await file_saver.save_qa_pair(question, answer)

    print(f"{say_func_name()}\tIncoming message (question to ChatGPT):\t{question}")
    print(f"{say_func_name()}\tLoad Prompt (for ChatGPT):\n`{prompt}`")
    print(f"{say_func_name()}\tSending message (temp answer at ChatGPT):\t{my_message}")
    print(f"{say_func_name()}\tSending message (answer at ChatGPT):\t{answer}")
    await paragraph()

    if len(answer) <= 4000:
        print(f'\n{"=" * 20}\nLength ({len(answer)})\n')
        # await temp_answer.edit_text(text=f"{answer}", parse_mode=util.ParseMode.MARKDOWN_V2)  # Глючит
        try:
            # await util.send_text(update=update, context=context, text=f'{answer}')
            await my_message.edit_text(text=f'{answer}', parse_mode=util.ParseMode.MARKDOWN)
            # await util.send_text(update=update, context=context, text=f'{answer}', parse_mode=util.ParseMode.MARKDOWN)
            # if my_message.text == message_text_wait:
            #     await util.delete_message(update=update, context=context, message=my_message)
        except Exception as e:
            print(f'\n{"=" * 20}\nLength ({len(answer)})\n\nAnswer:\n{answer}\n\n')
            await util.delete_message(update=update, context=context, message=my_message)
            await util.send_text(update=update, context=context, text=f'{answer}')
            await util.send_text(
                update=update, context=context,
                text=f'*ERROR: Exception:*\n\n{e}\n\n{"=" * 20}\nLength ({len(answer)})\n'
            )
    else:
        find_result = False
        find = '```'
        page = 0

        # await temp_answer.delete()
        chunks = await split_text_to_chunks(answer)
        for chunk in chunks:
            page = page + 1
            """
            # print(
            #     f"\n{'='*40}\n"
            #     f"Chunk ({len(chunks)}) (length {len(chunk)}/{len(answer)}): type: {type(chunks)}\n"
            #     f"{'='*40}\n"
            # )
            # print(f"{chunk}\n{'='*40}\n")
            """

            # Если больше 0
            if await count_triple_dashes(chunk, find) != 0:
                updated_chunk = find + chunk if find_result else chunk

                find_result = await count_triple_dashes_and_check(updated_chunk, find)
                updated_chunk = updated_chunk + find if find_result else updated_chunk
            else:
                updated_chunk = chunk

            try:
                await util.send_text(
                    update=update, context=context, text=f'*Page: {page}*\n\n{updated_chunk}')  # MARKDOWN_V2
            except Exception as e:
                await util.send_text(
                    update=update, context=context, text=f'*Page: {page}*\n\n{updated_chunk}'
                    # , parse_mode=util.ParseMode.HTML
                )
                print(f'Error: {e}')
                await util.send_text(
                    update=update, context=context,
                    text=f'*ERROR: Exception: Page: {page}*\n\n```\n{e}\n```\n{"=" * 20}\n'
                         f'Length chunk ({len(chunk)}) (Length answer: {len(answer)})\n'
                )
                await util.send_text(
                    update=update, context=context,
                    text=f'*ERROR: Exception: Page: {page}*\n\n{e}\n\n{"=" * 20}\n'
                         f'Length chunk ({len(chunk)}) (Length answer: {len(answer)})\n'
                )  # for test

            # await util.send_text(update=update, context=context, text=f"{chunk}", parse_mode=ParseMode.HTML)
            await aio_sleep(1)
            print(f"Chunk END\n{'=' * 40}\n")


async def gpt_models(update, context) -> None:
    mode = "gpt_models"
    rn = "\n"
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    # await util.send_photo(update=update, context=context, name=mode)
    await util.send_text(update=update, context=context, text=answer)

    answer = await chatgpt.get_models_list()
    await util.send_text(
        update=update, context=context,
        text=f"```\n{rn.join(map(str, sorted([model.id for model in answer.data])))}```"
    )

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    # Итерация по каждой модели в списке (в SyncPage)
    print(f'Sending message:\t\n{rn.join(map(str, sorted([model.id for model in answer.data])))}')
    print(f'List models:\t\n{sorted([model.id for model in answer.data])}')

    await paragraph()


async def date(update, context) -> None:
    mode = 'date'
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    delete_delay = 3

    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)
    
    my_buttons = await util.send_text_buttons(
        update=update, context=context, text=answer, buttons={
            'date_grande': 'Ариана Гранде',
            'date_robbie': 'Марго Робби',
            'date_zendaya': 'Зендея',
            'date_gosling': 'Райан Гослинг',
            'date_hardy': 'Том Харди',
        }
    )

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    print(f'{say_func_name()}\tSending message:\t{answer}')
    print(f'{say_func_name()}\tSending buttons:\t{my_buttons}')
    await paragraph()


async def date_dialog(update, context) -> None:
    question = update.message.text
    my_message = await util.send_text(update=update, context=context, text='*ChatGPT набирает текст...*')
    answer = await chatgpt.add_message(question)
    # await util.send_text(update=update, context=context, text=f"*{answer}*")
    await my_message.edit_text(f'{answer}')

    print(f'{say_func_name()}\tIncoming message (question to ChatGPT in Dialog):\t{question}')
    print(f'{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}')
    print(f'{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}')


async def date_button(update, context) -> None:
    mode = 'date'
    sex = {'grande': 'woman', 'robbie': 'woman', 'zendaya': 'woman', 'gosling': 'man', 'hardy': 'man'}
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await util.send_photo(update=update, context=context, name=query)

    """
    # Исправление ошибки при наличии в переменной {query} нижнего подчеркивания:
    util.send_text(update, context, f"{query}" parse_mode=util.ParseMode.HTML) 
    or util.send_text(update, context, f"`{query}`")
    """
    await util.send_text(
        update=update, context=context,
        text=f"Отличный выбор!\n"
             f"Пригласите {'девушку' if (sex[query[5:]] == 'woman') else 'парня'} на свидание, за 5 сообщений"
    )
    """
    # alternate:
    sex = {"man": {"gosling", "hardy"}, "woman": {"grande", "robbie", "zendaya"}}
    await util.send_text(
        update=update, context=context,
        text=f"Отличный выбор!\n
        Пригласите {'парня' if (query[5:] in sex['man']) else 'девушку'} на свидание, за 5 сообщений"
    )
    """

    if dialog.mode != mode:
        print(f'ERROR: Dialog Mode: {dialog.mode}')
        dialog.mode = mode
        print(f'Changed Dialog Mode: {dialog.mode}')

    prompt = util.load_prompt(name=query)
    chatgpt.set_prompt(prompt)

    print(f'{say_func_name()}\tPressed button ID:\t{query}')
    print(f'{say_func_name()}\tLoad Prompt (for ChatGPT):\n`{prompt}`')
    await paragraph()


async def message(update, context) -> None:
    mode = 'message'
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    delete_delay = 3
    
    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)

    my_buttons = await util.send_text_buttons(
        update=update, context=context, text=answer, buttons={
            'message_next': 'Следующее сообщение',
            'message_date': 'Пригласить на свидание',
        }
    )

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    print(f'{say_func_name()}\tSending message:\t{answer}')
    print(f'{say_func_name()}\tSending buttons:\t{my_buttons}')
    await paragraph()

    dialog.list.clear()


async def message_dialog(update, context) -> None:
    question = update.message.text
    dialog.list.append(question)

    print(f'{say_func_name()}\tIncoming message (added Dialog List for ChatGPT):\t{question}')
    print(f'{say_func_name()}\tAll messages in Dialog (All questions for ChatGPT in Dialog):\t{dialog.list}')
    # print(f'{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}')
    await paragraph()


async def message_button(update, context) -> None:
    query = update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку

    prompt = util.load_prompt(name=query)
    chatgpt.set_prompt(prompt)
    user_chat_history = '\n\n'.join(dialog.list)
    message_text_wait = '*ChatGPT думает над вариантами ответа...*'
    my_message = await util.send_text(update=update, context=context, text=message_text_wait)
    answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_chat_history)
    
    try:
        await my_message.edit_text(text=f'{answer}', parse_mode=util.ParseMode.MARKDOWN)
        
        # if my_message.text == message_text_wait:
        #     await util.delete_message(update=update, context=context, message=my_message)
        # await util.send_text(update=update, context=context, text=f'{answer}', parse_mode=util.ParseMode.MARKDOWN)
    except Exception as e:
        print(f'\n{"=" * 20}\nLength ({len(answer)})\n\nAnswer:\n{answer}\n\n')
        await util.delete_message(update=update, context=context, message=my_message)
        await util.send_text(update=update, context=context, text=f'{answer}')
        await util.send_text(
            update=update, context=context,
            text=f'*ERROR: Exception:*\n\n{e}\n\n{"=" * 20}\nLength ({len(answer)})\n'
        )

    print(f'{say_func_name()}\tPressed button ID:\t{query}')
    print(f'{say_func_name()}\tIncoming messages in Dialog (All questions for ChatGPT in Dialog):\t{dialog.list}')
    print(f'{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}')
    print(f'{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}')
    await paragraph()


async def profile(update, context) -> None:
    mode = 'profile'
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    delete_delay = 3
    
    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)

    dialog.count = 0
    await util.send_text(update=update, context=context, text='Сколько Вам лет?')

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    print(f'{say_func_name()}\tSending message:\t{answer}')
    # print(f'{say_func_name()}\tSending buttons:\t{my_buttons}')
    await paragraph()

    dialog.list.clear()
    dialog.user.clear()


async def profile_dialog(update, context) -> None:
    question = update.message.text
    dialog.count += 1

    print(
        f'{say_func_name()}\tDialog Count: {dialog.count}\tIncoming message (question to ChatGPT in Dialog): {question}'
    )

    if dialog.count == 1:
        dialog.user['age'] = question
        await util.send_text(update=update, context=context, text='Кем Вы работаете?')
    elif dialog.count == 2:
        dialog.user['occuration'] = question
        await util.send_text(update=update, context=context, text='У Вас есть хобби?')
    elif dialog.count == 3:
        dialog.user['hobby'] = question
        await util.send_text(update=update, context=context, text='Что Вам НЕ нравится в людях?')
    elif dialog.count == 4:
        dialog.user['annoys'] = question
        await util.send_text(update=update, context=context, text='Цель знакомства?')
    elif dialog.count == 5:
        dialog.user['goals'] = question

        prompt = util.load_prompt(name=dialog.mode)
        user_info = util.dialog_user_info_to_str(user=dialog.user)

        my_message = await util.send_text(update=update, context=context, text='*ChatGPT обрабатывает Ваши данные...*')
        answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_info)
        await my_message.edit_text(text=f'{answer}')

        print(f'{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}')
        print(f'{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}')


async def opener(update, context) -> None:
    mode = 'opener'
    dialog.mode = mode
    question = update.message.text
    answer = util.load_message(name=mode)
    delete_delay = 3
    
    await welcome_message_with_delayed_deletion(update, context, name=mode, text=answer, delay=delete_delay)

    dialog.count = 0
    await util.send_text(update=update, context=context, text='Имя девушки?')

    print(f'{say_func_name()}\tIncoming message:\t{question}')
    print(f'{say_func_name()}\tChanged Dialog Mode:\t{dialog.mode}')
    print(f'{say_func_name()}\tSending message:\t{answer}')
    # print(f'{say_func_name()}\tSending buttons:\t{my_buttons}')
    await paragraph()

    dialog.list.clear()
    dialog.user.clear()


async def opener_dialog(update, context) -> None:
    question = update.message.text
    dialog.count += 1

    print(
        f'{say_func_name()}\tDialog Count: {dialog.count}\tIncoming message (question to ChatGPT in Dialog): {question}'
    )

    if dialog.count == 1:
        dialog.user['name'] = question
        await util.send_text(update=update, context=context, text='Сколько ей лет?')
    elif dialog.count == 2:
        dialog.user['age'] = question
        await util.send_text(update=update, context=context, text='Оцените ее внешность: 1-10 баллов?')
    elif dialog.count == 3:
        dialog.user['handsome'] = question
        await util.send_text(update=update, context=context, text='Кем она работает?')
    elif dialog.count == 4:
        dialog.user['occupation'] = question
        await util.send_text(update=update, context=context, text='Цель знакомства?')
    elif dialog.count == 5:
        dialog.user['goals'] = question

        prompt = util.load_prompt(name=dialog.mode)
        user_info = util.dialog_user_info_to_str(user=dialog.user)

        my_message = await util.send_text(update=update, context=context, text='*ChatGPT обрабатывает Ваши данные...*')
        answer = await chatgpt.send_question(prompt_text=prompt, message_text=user_info)
        await my_message.edit_text(text=f'{answer}')

        print(f'{say_func_name()}\tSending message (temp answer in Dialog):\t{my_message}')
        print(f'{say_func_name()}\tSending message (answer at ChatGPT in Dialog):\t{answer}')


async def hello(update, context) -> None:
    if update.message:
        question = update.message.text
        answer = '*Привет!*\nТут могла бы быть твоя реклама! =)\nНо, возможно, Вам нужен ChatGPT /gpt?!'
        delete_delay = 3
        
        print(f'{"=" * 40}\n{say_func_name()}\tDialog Mode:\t{dialog.mode}')

        if dialog.mode is not None and dialog.mode != 'main':
            print(f'{say_func_name()}\tSelect Dialog Function:\t{dialog.mode}_dialog')
            await globals()[f'{dialog.mode}_dialog'](update=update, context=context)
        else:
            await welcome_message_with_delayed_deletion(
                update, context, text=answer, delay=delete_delay, delete_init=False)
            """
            # Old version:
            await util.send_text(update=update, context=context, text="*Привет!*")
            await sleep()
            await util.send_text(update=update, context=context, text="Как дела?!")
            await sleep()
            await util.send_text(update=update, context=context, text=f"Вы написали: {question}")
            await sleep()
            await util.send_photo(update=update, context=context, name="avatar_main")
            await sleep()
            await util.send_text_buttons(
                update=update, context=context, text="Запустить процесс?", buttons={
                    "prc_start": " Запустить ",
                    "prc_stop": " Остановить "
                }
            )
            """

        print(f"{say_func_name()}\tIncoming message:\t{question}")
        await paragraph()
    else:
        answer = 'Что-то пошло не так, попробуйте еще раз!'
        await util.send_text(update=update, context=context, text=answer)


async def hello_button(update, context) -> None:
    query = await update.callback_query.data  # код кнопки
    await update.callback_query.answer()  # помечаем что обработали нажатие на кнопку
    await util.send_text(
        update=update, context=context, text=f"Процесс {'запущен' if 'start' in query != -1 else 'остановлен'}")

    print(f"{say_func_name()}\tPressed button ID:\t{query}")
    await paragraph()


async def split_text_to_chunks(text: str, chunk_size: int = 4096) -> list:
    """
    Асинхронно разбивает текст на части, не превышающие chunk_size символов.

    :param text: Исходный текст для разбивки.
    :param chunk_size: Максимальный размер одной части.
    :return: Список текстовых блоков.
    """
    if len(text) < chunk_size:
        return [text]

    chunks = []
    pos_start = 0
    length = len(text)

    while pos_start < length:
        end = pos_start + chunk_size
        if end >= length:
            chunks.append(text[pos_start:])
            break

        # Найдем последнее место переноса строки до лимита в chunk_size символов
        newline_index = text.rfind('\n', pos_start, end)

        if newline_index != -1:
            chunks.append(text[pos_start:newline_index + 1])
            pos_start = newline_index + 1
        else:
            # Если не найден перенос строки, разбиваем принудительно
            chunks.append(text[pos_start:end])
            pos_start = end

        # Симуляция асинхронной задачи, если необходимо
        # await sleep(0)

    return chunks


def initialize_chatgpt_service():
    config_gpt = get_config_gpt()
    
    # while not token_manager.get_update_status():
        # config_gpt = get_config_gpt()
        # token_manager.set_token(config_gpt['OPEN_AI_TOKEN'])
    
    if token_manager.set_token():
        return ai.ChatGptService(
            token=token_manager.get_token(), proxy=config_env['HTTP_PROXY'], timeout=config_gpt['timeout'],
            model=config_gpt['model'], max_tokens=config_gpt['max_tokens'], temperature=config_gpt['temperature']
        )
    else:
        return None


def main():
    # Инициализируем ChatGptService с токеном из TokenManager
    app = ApplicationBuilder().token(token=config_env['TELEGRAM_BOT_TOKEN']).build()
    
    app.add_handler(CommandHandler(command='start', callback=start))
    app.add_handler(CommandHandler(command='gpt', callback=gpt))
    app.add_handler(CommandHandler(command='gpt_models', callback=gpt_models))
    app.add_handler(CommandHandler(command='date', callback=date))
    app.add_handler(CommandHandler(command='message', callback=message))
    app.add_handler(CommandHandler(command='profile', callback=profile))
    app.add_handler(CommandHandler(command='opener', callback=opener))
    
    app.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=hello))
    # app.add_handler(MessageHandler(filters=filters.TEXT, callback=handle_message))
    app.add_handler(CallbackQueryHandler(callback=date_button, pattern='^date_.*'))
    app.add_handler(CallbackQueryHandler(callback=message_button, pattern='^message_.*'))
    app.add_handler(CallbackQueryHandler(callback=hello_button))
    
    app.run_polling()


if __name__ == '__main__':
    # Создаем функцию-хранилище
    storage_function = create_storage()

    dialog = util.Dialog()
    dialog.mode = None
    dialog.list = []
    dialog.count = 0
    dialog.user = {}

    config_env = get_config_env()

    folder_name = config_env['QA_FOLDER']
    file_saver = saver.AsyncFileSaver(folder_name)

    token_manager = token_mgr.TokenManager(config_env['OPEN_AI_TOKENS'])

    chatgpt = initialize_chatgpt_service()
    
    main()
    