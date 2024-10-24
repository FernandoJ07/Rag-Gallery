import pydantic_settings


class Configs(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    openai_api_key: str
    model: str
    max_tokens: int
    temperature: float
    number_of_vectorial_results: int
    url_mongodb: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
