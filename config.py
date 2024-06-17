import os
from dotenv import load_dotenv

# take environment variables from .env.
load_dotenv()

env = {
    'TELEGRAM_BOT_TOKEN': os.environ['TELEGRAM_BOT_TOKEN'],
    'OPEN_AI_TOKEN': os.environ['OPEN_AI_TOKEN'],
    'HTTP_PROXY': os.environ['HTTP_PROXY'],
}


if __name__ == '__main__':
    print(
        f"env:\n{env['TELEGRAM_BOT_TOKEN']}\n\n"
        f"os.environ:\n{os.environ['TELEGRAM_BOT_TOKEN']}\n\n"
        f"os.getenv:\n{os.getenv('TELEGRAM_BOT_TOKEN')}\n\n"
    )
    print(f"os.environ:\n{os.environ}\n\n")
