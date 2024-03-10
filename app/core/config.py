from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    # Всё это не спрятано в .env из-за тестов
    app_title: str = 'КРАУДФАНДИНГОВАЯ ПЛАТФОРМА'
    descriptions: str = ('Это проект для пожертвования на'
                         'нужды кошачьего приюта!!!')
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    # Переменные для Google API
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    class Config:
        env_file = '.env'


settings = Settings()
