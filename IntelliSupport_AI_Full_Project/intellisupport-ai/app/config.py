from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    app_secret_key: str = "development-only-change-me"
    database_url: str = "sqlite:///./intellisupport.db"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = ""
    rag_embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    allow_first_user_admin: bool = True
    cors_origins: str = "http://127.0.0.1:8000,http://localhost:8000"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
