import os
from pathlib import Path

from pydantic import BaseModel, field_validator

BASE_DIR = Path(__file__).resolve().parent.parent


class AuthJWT(BaseModel):
    """
    base config for jwt information
    """
    public_key_path: str
    private_key_path: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int
    token_type_field: str


class DBConfig(BaseModel):
    database_host: str
    database_port: int
    database_username: str
    database_password: str
    database_name: str


class Config(BaseModel):
    verification_code_time_expiration: int
    project_host: str
    jwt: AuthJWT

    @field_validator("project_host")
    def validate_host(cls, value):
        if value.endswith("/"):
            raise Exception("Config: project_host should be without /")
        return value


def load_config() -> Config:
    """
    return config in modules that requires settings
    :return: config with all parameters
    """
    return Config(
        verification_code_time_expiration=60 * 5,
        project_host="http://localhost:8000",
        jwt=AuthJWT(
            public_key_path=Path(os.path.join(BASE_DIR.parent, "certs", "jwt-public.pem")).read_text(),
            private_key_path=Path(os.path.join(BASE_DIR.parent, "certs", "jwt-private.pem")).read_text(),
            algorithm="RS256",
            access_token_expire_minutes=5,
            refresh_token_expire_days=10,
            token_type_field="token_type"
        ),
    )


def __load_db_config() -> DBConfig:
    return DBConfig(
        database_host=os.getenv("DATABASE_HOST"),
        database_port=os.getenv("DATABASE_PORT"),
        database_username=os.getenv("DATABASE_USERNAME"),
        database_password=os.getenv("DATABASE_PASSWORD"),
        database_name=os.getenv("DATABASE_NAME"),
    )


db_config: DBConfig = __load_db_config()
