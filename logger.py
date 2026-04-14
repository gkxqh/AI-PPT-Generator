import datetime


def get_timestamp():
    """
    获取当前时间戳
    
    Returns:
        str: 格式化的时间戳
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def info(message):
    """
    输出信息日志
    
    Args:
        message: 日志消息
    """
    print(f"[{get_timestamp()}] [INFO] {message}")


def success(message):
    """
    输出成功日志
    
    Args:
        message: 日志消息
    """
    print(f"[{get_timestamp()}] [SUCCESS] {message}")


def warning(message):
    """
    输出警告日志
    
    Args:
        message: 日志消息
    """
    print(f"[{get_timestamp()}] [WARNING] {message}")


def error(message):
    """
    输出错误日志
    
    Args:
        message: 日志消息
    """
    print(f"[{get_timestamp()}] [ERROR] {message}")


def step(step_num, message):
    """
    输出步骤日志
    
    Args:
        step_num: 步骤编号
        message: 步骤描述
    """
    print(f"[{get_timestamp()}] [STEP {step_num}] {message}")
