from dotenv import load_dotenv
import os

load_dotenv()  # Carga las variables del archivo .env


class Settings:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    bot_token = os.getenv("BOT_ADMIN")
    database_url = os.getenv("DATABASE_URL")


settings = Settings()
