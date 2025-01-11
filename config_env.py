from os import getenv
from os.path import dirname, abspath, join, exists
from enum import Enum
from typing import Optional


class EnvEnum(Enum):
    DEV = 'dev'
    TEST = 'test'
    PROD = 'prod'


ENVS = list(map(lambda x: getattr(EnvEnum, x).value, filter(lambda x: not x.startswith('__'), dir(EnvEnum))))

# 运行环境
PROJECT_ROOT = dirname(__file__)
RUNENV = getenv('RUNENV', EnvEnum.DEV.value).lower()
IS_PROD: bool = RUNENV == EnvEnum.PROD.value
IS_DEV: bool = RUNENV == EnvEnum.DEV.value
IS_TEST: bool = RUNENV == EnvEnum.TEST.value
CHANGE_THIS = 'change-this'


def _get_env_file() -> Optional[str]:
    ENV_FILE_MAP = dict(map(lambda x: (x.value, f'.env.{x.value}'), EnvEnum))
    filename = ENV_FILE_MAP.get(RUNENV, ENV_FILE_MAP[EnvEnum.DEV.value])
    return abspath(join(PROJECT_ROOT, filename))


ENV_FILE = _get_env_file()
ENV_DIR = dirname(ENV_FILE)


def check_env_exists(env_file: str) -> None:
    return exists(env_file)
