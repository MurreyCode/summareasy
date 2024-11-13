from pydantic import BaseSettings

class Settings(BaseSettings):
    # Gmail API settings
    gmail_client_secret: str
    gmail_token_file: str = 'token.json'
    
    # SQLite Database
    database_url: str = 'sqlite:///summareasy.db'
    
    class Config:
        env_file = '.env'

settings = Settings()
