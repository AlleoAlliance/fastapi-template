import threading
import time


def _get_worker_id():
    tid = threading.get_ident()
    worker_id = tid % 1024  # 限制 worker_id 范围
    return worker_id


def _current_timestamp():
    """获取当前时间戳（毫秒级）"""
    return int(time.time() * 1000)


def _wait_for_next_timestamp(last_timestamp):
    """等待直到下一毫秒"""
    timestamp = _current_timestamp()
    while timestamp <= last_timestamp:
        timestamp = _current_timestamp()
    return timestamp


class UniqueIDGenerator:
    def __init__(self, worker_id, data_center_id=0):
        # 初始配置
        self.worker_id = worker_id  # 唯一机器标识符
        self.data_center_id = data_center_id  # 数据中心标识符，默认为 0
        self.sequence = 0  # 毫秒内的序列号
        self.last_timestamp = -1  # 上次生成 ID 的时间戳

        # 各种配置参数
        self.worker_id_bits = 5  # 工作机器标识符占用 5 位
        self.data_center_id_bits = 5  # 数据中心标识符占用 5 位
        self.sequence_bits = 12  # 序列号占用 12 位

        # 各部分的最大值
        self.max_worker_id = (1 << self.worker_id_bits) - 1  # 31
        self.max_data_center_id = (1 << self.data_center_id_bits) - 1  # 31
        self.max_sequence = (1 << self.sequence_bits) - 1  # 4095

        # 时间戳的偏移量，设为自定义起始时间（如 2020-01-01）
        self.start_timestamp = 1609459200000  # 2021-01-01 00:00:00（毫秒）

        # 位移量
        self.worker_id_shift = self.sequence_bits
        self.data_center_id_shift = self.sequence_bits + self.worker_id_bits
        self.timestamp_shift = self.sequence_bits + self.worker_id_bits + self.data_center_id_bits

        # 53 位掩码
        self.mask = 0x1FFFFFFFFFFFFF  # 53 位最大值

        self.lock = threading.Lock()  # 锁，确保线程安全

    def generate_id(self):
        """生成唯一 ID"""
        with self.lock:
            timestamp = _current_timestamp()

            if timestamp == self.last_timestamp:
                # 同一毫秒内，递增序列号
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    # 序列号用尽，等待下一毫秒
                    timestamp = _wait_for_next_timestamp(self.last_timestamp)
            else:
                self.sequence = 0  # 不同毫秒内，重置序列号

            if timestamp < self.last_timestamp:
                raise Exception('Clock moved backwards. Refusing to generate id.')

            self.last_timestamp = timestamp

            # 组合各个部分生成最终的 ID
            id_ = (
                ((timestamp - self.start_timestamp) << self.timestamp_shift)
                | (self.data_center_id << self.data_center_id_shift)
                | (self.worker_id << self.worker_id_shift)
                | self.sequence
            )

            # 对 ID 进行掩码，确保不超过 53 位
            id_ &= self.mask

            return id_


# 创建生成器实例
generator = UniqueIDGenerator(_get_worker_id())


def get_next_id():
    return generator.generate_id()
