import asyncio
import os
from typing import AsyncGenerator, TypeVar
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select, MetaData
from config import settings

async_engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    pool_recycle=3600,  # 每小时回收连接
    pool_pre_ping=True,  # 启用连接检查
    echo=settings.IS_PRINT_SQL,  # 是否打印SQL语句
)
# 创建 AsyncSessionLocal 类，用于数据库会话管理
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=async_engine, class_=AsyncSession)

metadata = MetaData()

TableBase = declarative_base(metadata=metadata)
T_TableBase = TypeVar('T_TableBase', bound=TableBase)


@asynccontextmanager
async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async_db: AsyncSession = AsyncSessionLocal()
    try:
        async with async_db.begin():  # 自动管理事务
            yield async_db
    finally:
        await async_db.close()


@asynccontextmanager
async def get_test_async_db():
    DB_URI = settings.TEST_DATABASE_URL
    # 创建异步引擎
    engine = create_async_engine(DB_URI, future=True, echo=settings.IS_PRINT_SQL)
    TestAsyncSession = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with TestAsyncSession() as async_session:
        # async with engine.begin() as conn:
        #     await conn.run_sync(lambda c: print(inspect(c).get_table_names()))
        yield async_session
    # 清理测试数据库
    if settings.TEST_DB_ONCE:
        async with engine.begin() as conn:
            await conn.run_sync(metadata.drop_all)
        await engine.dispose()
        await asyncio.sleep(0.1)  # 等待引擎关闭
        # 删除测试数据库文件
        if 'sqlite' in DB_URI and ':memory:' not in DB_URI:
            db_file = DB_URI.split('///').pop()
            if os.path.exists(db_file):
                os.remove(db_file)


__all__ = [
    'get_async_db',
    'get_test_async_db',
    'async_engine',
    'TableBase',
    'T_TableBase',
    'AsyncSessionLocal',
    'AsyncSession',
    'select',
    'metadata',
]
