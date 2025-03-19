from utils.connect import get_async_db


async def get_adb():
    async with get_async_db() as db:
        yield db
