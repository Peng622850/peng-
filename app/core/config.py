from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.siliconflow.cn/v1"
    DEEPSEEK_MODEL: str = "deepseek-ai/DeepSeek-V2.5"
    AI_QUESTION_MAX_RETRIES: int = 2
    AI_QUESTION_TIMEOUT: int = 30

    class Config:
        env_file = ".env"

settings = Settings()