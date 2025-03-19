import pytest


def test_concurrent_get_next_id():
    from concurrent.futures import ThreadPoolExecutor
    from threading import Lock
    from utils.snowflake import get_next_id

    id_list = []
    lock = Lock()  # 确保对 id_list 的操作线程安全

    def worker():
        for _ in range(100):  # 每个线程生成 100 个 ID
            unique_id = get_next_id()
            with lock:
                id_list.append(unique_id)

    # 使用 ThreadPoolExecutor 模拟多线程并发
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(worker) for _ in range(100)]
        for future in futures:
            future.result()  # 等待所有任务完成

    # 检查是否有重复 ID
    if len(id_list) != len(set(id_list)):
        raise ValueError(f'有重复 ID！重复数量: {len(id_list) - len(set(id_list))}')


@pytest.mark.asyncio
async def test_redis_clt(rds):
    await rds.set('test_key', 'test_value', nx=1)
    value = await rds.get('test_key')
    assert value == 'test_value'
    await rds.delete('test_key')
    value = await rds.get('test_key')
    assert value is None
