import httpcore
import openai
from openai import OpenAI
import httpx as httpx
from tenacity import retry, stop_after_attempt, wait_fixed


class ChatGptService:
    client: OpenAI = None
    # message_list: list = None

    def __init__(
            self, token: str, proxy: str, timeout: int = 60, model: str = 'gpt-4o', max_tokens: int = 4096,
            temperature: float = 0.9
    ):
        self.token_src = token
        self.token = self._process_token()
        self.proxy = proxy
        self.timeout = timeout
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.message_list = []
        self._initialize_client()
        print(
            f'GPT Token:\t\t{self.token}\t{self.token[:7:-1]}\n'
            f'GPT Model:\t\t{self.model}\n'
            f'Max tokens:\t\t{self.max_tokens}\n'
            f'Temperature:\t{self.temperature}'
        )

    def _process_token(self):
        return f'sk-proj-{self.token_src[:3:-1]}' if self.token_src.startswith('gpt:') else self.token_src
    
    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def _initialize_client(self):
        try:
            # Initialize the OpenAI client
            self.client = openai.OpenAI(
                http_client=httpx.Client(proxies=self.proxy, timeout=httpx.Timeout(self.timeout)), api_key=self.token
            )
            print('HTTP Client for OpenAI initialized successfully.')
        except (httpx.ConnectError, httpcore.ConnectError) as e:
            print(f'ERROR: Failed to initialize HTTP Client for OpenAI: "{e}". Retrying...')
            raise  # Reraise exception to trigger retry
        except Exception as e:
            print(f'ERROR: An unexpected error occurred: "{e}".')
            # Handle other exceptions if necessary

    def update_token(self, new_token):
        self.token = self._process_token(new_token)
        self._initialize_client()

    async def send_message_list(self) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=self.message_list,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            message = completion.choices[0].message
            self.message_list.append(message)
            return message.content
        except openai.AuthenticationError:
            print('ERROR: OpenAI Authentication Error.')
            return 'Sorry, try again later.\tAuthentication Error!'
        except openai.RateLimitError:
            print('ERROR: OpenAI Rate Limit Error')
            return 'Sorry, try again later.\tRate Limit Error!'

    def set_prompt(self, prompt_text: str) -> None:
        self.message_list.clear()
        self.message_list.append({'role': 'system', 'content': prompt_text})

    async def add_message(self, message_text: str) -> str:
        self.message_list.append({'role': 'user', 'content': message_text})
        return await self.send_message_list()

    async def send_question(self, prompt_text: str, message_text: str) -> str:
        self.message_list.clear()
        self.message_list.append({'role': 'system', 'content': prompt_text})
        self.message_list.append({'role': 'user', 'content': message_text})
        return await self.send_message_list()

    async def get_models_list(self):
        return self.client.models.list()
