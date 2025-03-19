import warnings
from os import getenv
from typing import Optional, List
from typing_extensions import Self

from urllib.parse import quote

from pydantic import computed_field, model_validator, Field, ValidationError
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from config_env import ENV_FILE, CHANGE_THIS, PROJECT_ROOT, IS_DEV, IS_TEST, IS_PROD, RUNENV, EnvEnum

warnings.filterwarnings('ignore', category=UserWarning)


class MysqlSettingsMixin:
    # mysql connect info
    MYSQL_HOST: str = Field(title='mysql host', default='localhost')
    MYSQL_PORT: int = Field(title='mysql port', default=3306)
    MYSQL_USERNAME: str = Field(title='mysql username', default=CHANGE_THIS)
    MYSQL_PASSWORD: str = Field(title='mysql password', default=CHANGE_THIS)
    MYSQL_DB_NAME: str = Field(title='mysql db name', default=CHANGE_THIS)

    @computed_field
    @property
    def CHECK_FIELDS(self) -> List[str]:
        return ['MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DB_NAME', 'REDIS_PASSWORD']

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return MultiHostUrl.build(
            scheme='mysql+aiomysql',
            username=self.MYSQL_USERNAME,
            password=self.MYSQL_PASSWORD,
            host=self.MYSQL_HOST,
            port=self.MYSQL_PORT,
            path=self.MYSQL_DB_NAME,
        ).unicode_string()


class RedisSettingsMixin:
    # redis connect info
    REDIS_HOST: str = Field(title='redis host', default='localhost')
    REDIS_PORT: int = Field(title='redis port', default=6379)
    REDIS_PASSWORD: Optional[str] = Field(title='redis password', default=None)
    REDIS_PATH: str = Field(title='redis path', default='0')

    @computed_field
    @property
    def REDIS_URI(self) -> str:
        return MultiHostUrl.build(
            scheme='redis',
            password=quote(self.REDIS_PASSWORD) if self.REDIS_PASSWORD else None,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
            path=self.REDIS_PATH,
        ).unicode_string()


class CommonSettings(BaseSettings):
    """
    当默认值设置为CHANGE_THIS时
    将会自动校验，必须要更改之后才能通过
    """

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

    JWT_ALGORITHM: str = Field(title='JWT 算法', default='HS256')
    JWT_SECRET_KEY: str = Field(title='JWT 密钥', default=CHANGE_THIS)
    JWT_ATK_EXP_DELTA: int = Field(title='access token 过期时间差', default=15 * 60)
    JWT_RTK_EXP_DELTA: int = Field(title='refresh token 过期时间差', default=7 * 24 * 60 * 60)

    @model_validator(mode='after')
    def _enforce_non_default_secrets(self) -> Self:
        for name, field in self.model_fields.items():
            if field.default != CHANGE_THIS:
                continue
            value = getattr(self, name, None)
            if value == CHANGE_THIS:
                message = f'配置项："{name}" 未设置，请检查环境变量或配置文件'
                raise ValueError(message)
        return self

    @computed_field
    @property
    def IS_PROD(self) -> bool:
        return IS_PROD

    @computed_field
    @property
    def IS_DEV(self) -> bool:
        return IS_DEV

    @computed_field
    @property
    def IS_TEST(self) -> bool:
        return IS_TEST

    @computed_field
    @property
    def PROJECT_ROOT(self) -> str:
        return PROJECT_ROOT

    @computed_field
    @property
    def ZERO_WORD(self) -> str:
        return '\u200b'

    @computed_field
    @property
    def IS_PRINT_SQL(self) -> bool:
        return not self.IS_PROD


class DevSettings(CommonSettings, MysqlSettingsMixin, RedisSettingsMixin): ...


class TestSettings(CommonSettings, RedisSettingsMixin):
    REDIS_PATH: str = '1'
    TEST_DATABASE_URL: str = Field(title='测试数据库连接', default='sqlite+aiosqlite:///test.db')
    TEST_DB_ONCE: bool = Field(title='测试数据库是否为一次性', default=True)

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return self.TEST_DATABASE_URL


class ProdSettings(CommonSettings, MysqlSettingsMixin, RedisSettingsMixin):
    REDIS_PATH: str = '2'

    @computed_field
    @property
    def CHECK_FIELDS(self) -> List[str]:
        return super().CHECK_FIELDS + ['MYSQL_USERNAME', 'MYSQL_PASSWORD', 'MYSQL_DB_NAME', 'REDIS_PASSWORD']


def get_settings_class(env: str = RUNENV):
    if env == EnvEnum.DEV.value:
        return DevSettings
    if env == EnvEnum.TEST.value:
        return TestSettings
    if env == EnvEnum.PROD.value:
        return ProdSettings
    raise RuntimeError(f'未知的运行环境: {env}，请检查环境变量 RUNENV 是否正确配置')


def get_settings():
    cls = get_settings_class()
    return cls()


try:
    settings = getenv('IGNORE_SETTINGS') is None and get_settings()
except ValidationError as e:
    import logging

    settings = None
    logging.error(f'配置项读取失败，请检查文件："{ENV_FILE}" 是否正确配置\n错误信息：{e.errors()[0]["msg"]}')

    exit(1)

__all__ = ['settings', 'get_settings_class', 'get_settings']
