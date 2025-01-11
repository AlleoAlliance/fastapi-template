import sys


# 自定义全局异常处理函数
def runtime_except_hook(exc_type, exc_value, exc_tb):
    # 只处理 RuntimeError 异常
    if exc_type is RuntimeError:
        return
    # 对其他异常使用默认处理
    sys.__excepthook__(exc_type, exc_value, exc_tb)


# 将自定义异常处理函数设置为全局异常处理
sys.excepthook = runtime_except_hook
