from typing import Coroutine
from threading import Thread
import asyncio


def safe_async(co: Coroutine):
    try:
        try:
            # 检查是否已有运行中的事件循环
            asyncio.get_running_loop()
        except RuntimeError:
            # 当前无事件循环，直接运行协程
            asyncio.run(co)
            return
        t = Thread(target=lambda: asyncio.run(co))
        t.start()
        t.join()
    except RuntimeError:
        pass
