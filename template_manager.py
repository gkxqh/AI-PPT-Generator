import json
import os
from logger import info, error

# 模板配置文件路径
TEMPLATE_FILE = "templates.json"


def load_templates():
    """
    加载模板配置
    
    Returns:
        dict: 模板配置字典
    """
    if os.path.exists(TEMPLATE_FILE):
        try:
            with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            error(f"加载模板文件失败: {e}")
            return get_default_templates()
    else:
        # 创建默认模板文件
        default = get_default_templates()
        save_templates(default)
        return default


def save_templates(templates):
    """
    保存模板配置
    
    Args:
        templates: 模板配置字典
    """
    try:
        with open(TEMPLATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(templates, f, indent=2, ensure_ascii=False)
        info("模板配置保存成功")
    except Exception as e:
        error(f"保存模板文件失败: {e}")


def get_default_templates():
    """
    获取默认模板配置
    
    Returns:
        dict: 默认模板配置
    """
    return {
        "templates": {
            "default": {
                "name": "默认简约",
                "description": "简洁干净的默认样式",
                "colors": {
                    "primary": "2E86AB",
                    "secondary": "A23B72",
                    "background": "FFFFFF",
                    "title": "1A1A2E",
                    "content": "333333",
                    "accent": "E94F37"
                },
                "title_slide": {
                    "title_font_size": 44,
                    "title_font_bold": True,
                    "title_color": "primary",
                    "background_color": "background"
                },
                "content_slide": {
                    "title_font_size": 32,
                    "title_font_bold": True,
                    "title_color": "primary",
                    "bullet_font_size": 18,
                    "bullet_color": "content",
                    "content_font_size": 16,
                    "content_color": "666666",
                    "key_message_font_size": 20,
                    "key_message_color": "accent",
                    "background_color": "background"
                },
                "styles": {
                    "bullet_style": "disc",
                    "use_gradient": False,
                    "use_shadow": False
                }
            }
        },
        "current_template": "default"
    }


def get_template(template_id):
    """
    获取指定模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        dict: 模板配置
    """
    templates = load_templates()
    return templates.get("templates", {}).get(template_id)


def get_current_template():
    """
    获取当前使用的模板
    
    Returns:
        dict: 当前模板配置
    """
    # 优先从 config.json 读取
    try:
        from config import get_config
        config = get_config()
        current_id = config.get('template', {}).get('current', 'default')
    except:
        # 回退到 templates.json
        templates = load_templates()
        current_id = templates.get("current_template", "default")
    
    return get_template(current_id)


def set_current_template(template_id):
    """
    设置当前使用的模板
    
    Args:
        template_id: 模板ID
    
    Returns:
        bool: 是否设置成功
    """
    templates = load_templates()
    
    if template_id not in templates.get("templates", {}):
        error(f"模板 '{template_id}' 不存在")
        return False
    
    # 更新 templates.json
    templates["current_template"] = template_id
    save_templates(templates)
    
    # 同时更新 config.json
    from config import update_config
    update_config("template.current", template_id)
    
    info(f"已切换到模板: {templates['templates'][template_id]['name']}")
    return True


def list_templates():
    """
    列出所有可用模板
    
    Returns:
        list: 模板列表
    """
    templates = load_templates()
    template_list = []
    
    for template_id, template_data in templates.get("templates", {}).items():
        template_list.append({
            "id": template_id,
            "name": template_data.get("name", template_id),
            "description": template_data.get("description", ""),
            "is_current": template_id == templates.get("current_template")
        })
    
    return template_list


def hex_to_rgb(hex_color):
    """
    将十六进制颜色转换为RGB元组
    
    Args:
        hex_color: 十六进制颜色字符串（如 "FF0000" 或 "#FF0000"）
    
    Returns:
        tuple: RGB元组 (R, G, B)
    """
    # 移除 # 前缀
    hex_color = hex_color.lstrip('#')
    
    # 转换为RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_color(template, color_key):
    """
    从模板获取颜色（转换为RGB）
    支持两种方式：
    1. 引用方式：color_key = "primary" -> 从colors字典查找
    2. 直接值：color_key = "FF0000" -> 直接使用
    
    Args:
        template: 模板配置
        color_key: 颜色键名或十六进制颜色值
    
    Returns:
        tuple: RGB元组
    """
    colors = template.get("colors", {})
    
    # 检查是否是直接的十六进制颜色值（6位或7位，可能带#）
    if color_key and len(color_key) >= 6:
        # 移除可能的 # 前缀
        test_key = color_key.lstrip('#')
        # 检查是否全是十六进制字符
        if len(test_key) == 6 and all(c in '0123456789ABCDEFabcdef' for c in test_key):
            return hex_to_rgb(color_key)
    
    # 否则作为引用从colors字典查找
    hex_color = colors.get(color_key, "000000")
    return hex_to_rgb(hex_color)


def print_templates():
    """
    打印所有模板列表
    """
    templates = list_templates()
    
    print("\n" + "=" * 50)
    print("可用模板列表")
    print("=" * 50)
    
    for template in templates:
        current_marker = " (当前使用)" if template["is_current"] else ""
        print(f"\nID: {template['id']}{current_marker}")
        print(f"名称: {template['name']}")
        print(f"描述: {template['description']}")
    
    print("\n" + "=" * 50)


def add_custom_template(template_id, name, description, colors, styles=None):
    """
    添加自定义模板
    
    Args:
        template_id: 模板ID
        name: 模板名称
        description: 模板描述
        colors: 颜色配置
        styles: 样式配置（可选）
    
    Returns:
        bool: 是否添加成功
    """
    templates = load_templates()
    
    if template_id in templates.get("templates", {}):
        error(f"模板 '{template_id}' 已存在")
        return False
    
    # 创建新模板
    new_template = {
        "name": name,
        "description": description,
        "colors": colors,
        "title_slide": {
            "title_font_size": 44,
            "title_font_bold": True,
            "title_color": "primary",
            "background_color": "background"
        },
        "content_slide": {
            "title_font_size": 32,
            "title_font_bold": True,
            "title_color": "primary",
            "bullet_font_size": 18,
            "bullet_color": "content",
            "content_font_size": 16,
            "content_color": "666666",
            "key_message_font_size": 20,
            "key_message_color": "accent",
            "background_color": "background"
        },
        "styles": styles or {
            "bullet_style": "disc",
            "use_gradient": False,
            "use_shadow": False
        }
    }
    
    templates["templates"][template_id] = new_template
    save_templates(templates)
    info(f"模板 '{name}' 添加成功")
    return True
