import os
from datetime import datetime
import aiofiles


class AsyncFileSaver:
    """
    Класс для сохранения вопросов к ChatGPT и ответов на них.
    """
    def __init__(self, folder_name):
        self.folder_name = folder_name

    async def _ensure_folder_exists(self):
        if not os.path.exists(self.folder_name):
            os.makedirs(self.folder_name)

    async def save_qa_pair(self, question, answer):
        await self._ensure_folder_exists()

        current_date_and_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        file_name = f"qa_{current_date_and_time}.txt"
        file_path = os.path.join(self.folder_name, file_name)

        async with aiofiles.open(file_path, 'a', encoding='utf-8') as file:
            # Проверяем, если файл пустой, то записываем вопрос и разделитель
            if os.path.getsize(file_path) == 0:
                await file.write(question)
                await file.write(f"\n\n{'=' * 50}\n\n")
            # Записываем текст из переменной answer
            await file.write(answer)

        print(f"Содержимое переменных 'question' и 'answer' сохранено в файл: {file_path}")


# import os
# from datetime import datetime
# import aiofiles
# import aiofiles.os
#
#
# class AsyncFileSaver:
#     def __init__(self, folder_name):
#         self.folder_name = folder_name
#
#     async def _ensure_folder_exists(self):
#         if not await aiofiles.os.path.exists(self.folder_name):
#             await aiofiles.os.makedirs(self.folder_name)
#
#     async def save_qa_pair(self, question, answer):
#         await self._ensure_folder_exists()
#
#         current_date_and_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#         file_name = f"qa_{current_date_and_time}.txt"
#         file_path = os.path.join(self.folder_name, file_name)
#
#         async with aiofiles.open(file_path, 'w', encoding='utf-8') as file:
#             # Записываем текст из переменной question
#             await file.write(question)
#             # Записываем разделитель
#             await file.write(f"\n\n{'=' * 50}\n\n")
#             # Записываем текст из переменной answer
#             await file.write(answer)
#
#         print(f"Содержимое переменных 'question' и 'answer' сохранено в файл: {file_path}")


# import os
# from datetime import datetime
#
#
# class FileSaver:
#     def __init__(self, folder_name):
#         self.folder_name = folder_name
#         self._ensure_folder_exists()
#
#     def _ensure_folder_exists(self):
#         if not os.path.exists(self.folder_name):
#             os.makedirs(self.folder_name)
#
#     def save_answer(self, answer):
#         current_date_and_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
#         file_name = f"answer_{current_date_and_time}.txt"
#         file_path = os.path.join(self.folder_name, file_name)
#
#         with open(file_path, 'w', encoding='utf-8') as file:
#             file.write(answer)
#
#         print(f"Содержимое переменной 'answer' сохранено в файл: {file_path}")
