from os import getenv
from typing import Optional
from typing_extensions import Self

from urllib.parse import quote

from pydantic import computed_field, model_validator, Field, ValidationError
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from config_env import ENV_FILE, CHANGE_THIS, PROJECT_ROOT, IS_DEV, IS_TEST, IS_PROD


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding='utf8',
        env_ignore_empty=True,
        extra='ignore',
    )
    PROJECT_NAME: str = Field(title='项目名称', default='fastapi-template')
    VERSION: str = Field(title='版本号', default='0.0.1')
    API_V1_PREFIX: str = Field(title='v1接口前缀', default='/api/v1')
    ENABLE_API_DOCS: bool = Field(title='是否启用接口文档', default=True)

    # mysql connect info
    MYSQL_HOST: str = Field(title='mysql host', default='localhost')
    MYSQL_PORT: int = Field(title='mysql port', default=3306)
    MYSQL_USERNAME: str = Field(title='mysql username', default=CHANGE_THIS)
    MYSQL_PASSWORD: str = Field(title='mysql password', default=CHANGE_THIS)
    MYSQL_DB_NAME: str = Field(title='mysql db name', default=CHANGE_THIS)

    @computed_field
    @property
    def ZERO_WORD(self) -> str:
        return '\u200b'

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        if self.IS_TEST:
            return self.TEST_DATABASE_URL
        return MultiHostUrl.build(
            scheme='mysql+aiomysql',
            username=self.MYSQL_USERNAME,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB_NAME,
        ).unicode_string()

    # redis connect info
    REDIS_HOST: str = Field(title='redis host', default='localhost')
    REDIS_PORT: int = Field(title='redis port', default=6379)
    REDIS_PASSWORD: str = Field(title='redis password', default=CHANGE_THIS)

    @computed_field
    @property
    def REDIS_URI(self) -> str:
        return MultiHostUrl.build(
            scheme='redis',
            password=quote(self.REDIS_PASSWORD),
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path='1' if self.IS_TEST else '0',
        ).unicode_string()

    JWT_ALGORITHM: str = Field(title='JWT 算法', default='HS256')
    JWT_SECRET_KEY: str = Field(title='JWT 密钥', default=CHANGE_THIS)
    JWT_ATK_EXP_DELTA: int = Field(title='access token 过期时间差', default=15 * 60)
    JWT_RTK_EXP_DELTA: int = Field(title='refresh token 过期时间差', default=7 * 24 * 60 * 60)
    TEST_DATABASE_URL: str = Field(title='测试数据库连接', default='sqlite+aiosqlite:///test.db')
    TEST_DB_ONCE: bool = Field(title='测试数据库是否为一次性', default=True)

    def _check_default_secret(self, var_name: str, value: Optional[str]) -> Self:
        if value == CHANGE_THIS:
            message = f'配置项："{var_name}" 未设置，请检查环境变量或配置文件'
            raise ValueError(message)
        return self

    @model_validator(mode='after')
    def _enforce_non_default_secrets(self) -> Self:
        if not self.IS_TEST:
            self._check_default_secret('MYSQL_USERNAME', self.MYSQL_USERNAME)
            self._check_default_secret('MYSQL_PASSWORD', self.MYSQL_PASSWORD)
        self._check_default_secret('REDIS_PASSWORD', self.REDIS_PASSWORD)
        self._check_default_secret('JWT_SECRET_KEY', self.JWT_SECRET_KEY)
        return self

    @property
    def IS_PROD(self) -> bool:
        return IS_PROD

    @property
    def IS_DEV(self) -> bool:
        return IS_DEV

    @property
    def IS_TEST(self) -> bool:
        return IS_TEST

    @property
    def PROJECT_ROOT(self) -> str:
        return PROJECT_ROOT


def get_settings():
    return Settings()


try:
    settings = getenv('IGNORE_SETTINGS') is None and get_settings()
except ValidationError as e:
    from fastapi.logger import logger

    settings = None
    logger.error(f'配置项读取失败，请检查文件："{ENV_FILE}" 是否正确配置\n错误信息：{e.errors()[0]["msg"]}')

    exit(1)

__all__ = ['settings', 'Settings', 'get_settings']
