import json
import os

# 配置文件路径
CONFIG_FILE = "config.json"

# 默认配置
DEFAULT_CONFIG = {
    "max_api_calls": 5,
    "models": {
        "outline": "glm-5.1",
        "content": "glm-5.1"
    },
    "api": {
        "enable": True,
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "api_key": "YOUR_API_KEY_HERE"
    },
    "baidu_search": {
        "enable": True,
        "api_key": "YOUR_BAIDU_SEARCH_API_KEY_HERE"
    },
    "template": {
        "current": "default"
    }
}


def load_config():
    """
    加载配置文件
    
    Returns:
        dict: 配置字典
    """
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 验证配置结构
                return validate_config(config)
        except Exception as e:
            print(f"[配置错误] 加载配置文件失败: {e}")
            print("[配置错误] 使用默认配置")
            return DEFAULT_CONFIG
    else:
        # 配置文件不存在，创建默认配置
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG


def save_config(config):
    """
    保存配置到文件
    
    Args:
        config: 配置字典
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print("[配置] 配置保存成功")
    except Exception as e:
        print(f"[配置错误] 保存配置文件失败: {e}")


def validate_config(config):
    """
    验证配置结构，确保所有必要的键都存在
    
    Args:
        config: 配置字典
    
    Returns:
        dict: 验证后的配置
    """
    # 确保配置结构完整
    if "max_api_calls" not in config:
        config["max_api_calls"] = DEFAULT_CONFIG["max_api_calls"]
    
    if "models" not in config:
        config["models"] = DEFAULT_CONFIG["models"]
    
    if "api" not in config:
        config["api"] = DEFAULT_CONFIG["api"]
    
    if "baidu_search" not in config:
        config["baidu_search"] = DEFAULT_CONFIG["baidu_search"]
    
    if "template" not in config:
        config["template"] = DEFAULT_CONFIG["template"]
    
    # 确保models中的所有键都存在
    for key in DEFAULT_CONFIG["models"]:
        if key not in config["models"]:
            config["models"][key] = DEFAULT_CONFIG["models"][key]
    
    # 确保api中的所有键都存在
    for key in DEFAULT_CONFIG["api"]:
        if key not in config["api"]:
            config["api"][key] = DEFAULT_CONFIG["api"][key]
    
    # 确保baidu_search中的所有键都存在
    for key in DEFAULT_CONFIG["baidu_search"]:
        if key not in config["baidu_search"]:
            config["baidu_search"][key] = DEFAULT_CONFIG["baidu_search"][key]
    
    # 确保template中的所有键都存在
    for key in DEFAULT_CONFIG["template"]:
        if key not in config["template"]:
            config["template"][key] = DEFAULT_CONFIG["template"][key]
    
    return config


def get_config():
    """
    获取当前配置
    
    Returns:
        dict: 当前配置
    """
    return load_config()


def update_config(key_path, value):
    """
    更新配置
    
    Args:
        key_path: 键路径，例如 "models.outline"
        value: 新值
    """
    config = load_config()
    
    # 解析键路径
    keys = key_path.split('.')
    current = config
    
    # 导航到目标键
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # 更新值
    current[keys[-1]] = value
    
    # 保存配置
    save_config(config)


def reset_config():
    """
    恢复默认配置
    """
    save_config(DEFAULT_CONFIG)
    print("[配置] 已恢复默认配置")


def print_config():
    """
    打印当前配置
    """
    from template_manager import get_current_template
    
    config = load_config()
    print("\n===== 当前配置 =====")
    print(f"最大API调用次数: {config['max_api_calls']}")
    print("\n模型设置:")
    for model_type, model_name in config["models"].items():
        print(f"  {model_type}: {model_name}")
    print("\nAPI设置:")
    print(f"  启用API: {'是' if config['api']['enable'] else '否'}")
    print(f"  API基础URL: {config['api']['api_base']}")
    print(f"  API密钥: {config['api']['api_key']}")
    print("\n百度搜索设置:")
    print(f"  启用百度搜索: {'是' if config['baidu_search']['enable'] else '否'}")
    print(f"  百度搜索API密钥: {config['baidu_search']['api_key']}")
    
    # 显示当前模板
    try:
        current_template = get_current_template()
        print("\n模板设置:")
        print(f"  当前模板: {current_template.get('name', '默认模板')} ({config['template']['current']})")
    except:
        print("\n模板设置:")
        print(f"  当前模板: {config['template']['current']}")
    
    print("====================\n")


# 兼容旧的配置访问方式
config = load_config()
MAX_API_CALLS = config['max_api_calls']
MODEL_CONFIG = config['models']
API_CONFIG = config['api']
BAIDU_SEARCH_CONFIG = config['baidu_search']
