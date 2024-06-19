import openai
from openai import OpenAI
import httpx as httpx

from config import env as config_env


class ChatGptService:
    client: OpenAI = None
    message_list: list = None

    def __init__(self, token):
        token = "sk-proj-"+token[:3:-1] if token.startswith('gpt:') else token
        # print(f"GPT Token:\t{token}")
        self.client = openai.OpenAI(http_client=httpx.Client(proxies=config_env['HTTP_PROXY']), api_key=token)
        self.message_list = []

    async def send_message_list(self) -> str:
        try:
            completion = self.client.chat.completions.create(
                # Models: "gpt-3.5-turbo", "gpt-4o", "gpt-4-turbo"
                model="gpt-4-turbo",
                messages=self.message_list,
                max_tokens=3000,
                temperature=0.9
            )
            message = completion.choices[0].message
            self.message_list.append(message)
            return message.content
        except openai.AuthenticationError:
            print("OpenAI Authentication Error")
            return "Sorry, try again later."

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({"role": "system", "content": prompt_text})
        self.message_list.append({"role": "user", "content": message_text})
        return await self.send_message_list()
