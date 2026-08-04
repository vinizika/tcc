from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

class Settings:
    API_NAME = os.getenv("API_NAME")
    API_VERSION = os.getenv("API_VERSION")
    DEBUG = os.getenv("DEBUG") == "True"

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_DB = os.getenv("VECTOR_DB")
    ENVIRONMENT = os.getenv("ENVIRONMENT")

settings = Settings()