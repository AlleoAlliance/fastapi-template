import asyncio

import pytest
from typing import AsyncGenerator, Generator

from faker.providers import BaseProvider
from faker.proxy import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from redis.asyncio import Redis, from_url
from faker import Factory

from tests.helpers import sql_migrate
from config import settings
from utils.connect import get_test_async_db


class ChineseProdCodeProvider(BaseProvider):
    def product_code(self):
        return self.bothify('?####-#').upper()


@pytest.fixture(scope='session')
def event_loop() -> Generator:
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def db() -> AsyncGenerator[AsyncSession, None]:
    """创建数据库连接"""
    sql_migrate()
    async with get_test_async_db() as db:
        async with db.begin():  # 自动管理事务
            yield db


@pytest.fixture(scope='session')
async def rds() -> AsyncGenerator[Redis, None]:
    """创建redis客户端"""
    rc = from_url(settings.REDIS_URI, decode_responses=True)
    yield rc
    await rc.aclose()


@pytest.fixture(scope='module')
def client() -> Generator[TestClient, None, None]:
    """创建测试客户端"""
    from main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope='session')
def fake() -> Faker:
    _fake = Factory.create('zh_CN')
    _fake.add_provider(ChineseProdCodeProvider)
    return _fake


@pytest.fixture(scope='function')
def next_id():
    from utils.snowflake import get_next_id

    return get_next_id()
