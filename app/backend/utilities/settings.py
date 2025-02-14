from pydantic_settings import BaseSettings, SettingsConfigDict

class EnvSettings(BaseSettings):
    POSTGRESQL_URL: str
    ALGORITHM: str
    ALGORITHM_KEY: str
    DEBUG: bool

    model_config = SettingsConfigDict(env_file='.env',)


env_settings = EnvSettings()


