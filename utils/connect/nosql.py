import asyncio
import logging

import redis.asyncio as redis
from config import settings

__redis_client: redis.Redis = None


async def get_async_redis_connection() -> redis.Redis:
    global __redis_client
    try:
        if not __redis_client:
            __redis_client = await redis.from_url(settings.REDIS_URI, decode_responses=True)
        return __redis_client
    except redis.ConnectionError as e:
        logging.warning(f'Redis connect error, Retrying... \n{e}')
        await asyncio.sleep(3)
        return await get_async_redis_connection()


async def close_redis_connect():
    global __redis_client
    if __redis_client:
        await __redis_client.close()
        __redis_client = None


__all__ = ['get_async_redis_connection', 'close_redis_connect']
