from controller import run
from config import get_config, update_config, reset_config, print_config
from template_manager import list_templates, set_current_template, print_templates


def get_user_input():
    """
    获取用户输入的主题和页数
    
    Returns:
        tuple: (主题, 页数)
    """
    print("\n" + "=" * 50)
    print("请输入PPT生成参数")
    print("=" * 50)
    
    topic = input("请输入PPT主题: ").strip()
    if not topic:
        topic = "人工智能的发展历程与未来趋势"
        print(f"使用默认主题: {topic}")
    
    while True:
        num_slides_input = input("请输入目标页数 (默认8页，最少3页): ").strip()
        if not num_slides_input:
            num_slides = 8
            break
        try:
            num_slides = int(num_slides_input)
            if num_slides < 3:
                print("页数不能少于3页，已自动设为3页")
                num_slides = 3
            break
        except ValueError:
            print("请输入有效的数字")
    
    return topic, num_slides


def test_mode(topic, num_slides):
    """
    测试模式，直接使用给定的主题和页数
    
    Args:
        topic: PPT主题
        num_slides: 目标页数
    
    Returns:
        tuple: (主题, 页数)
    """
    print("\n" + "=" * 50)
    print("测试模式")
    print("=" * 50)
    print(f"使用测试主题: {topic}")
    print(f"使用测试页数: {num_slides}")
    return topic, num_slides


def show_template_menu():
    """
    显示模板选择菜单
    """
    print_templates()
    
    templates = list_templates()
    
    print("\n请选择模板ID（输入数字或ID名称）:")
    print("例如: 输入 '1' 或 'business'")
    print("输入 'q' 返回设置菜单")
    
    while True:
        choice = input("\n请选择: ").strip()
        
        if choice.lower() == 'q':
            return
        
        # 尝试按索引选择
        try:
            index = int(choice) - 1
            if 0 <= index < len(templates):
                template_id = templates[index]['id']
                if set_current_template(template_id):
                    print(f"\n✓ 已选择模板: {templates[index]['name']}")
                    return
                else:
                    print("模板切换失败，请重试")
            else:
                print(f"请输入 1-{len(templates)} 之间的数字")
        except ValueError:
            # 尝试按ID选择
            template_ids = [t['id'] for t in templates]
            if choice in template_ids:
                if set_current_template(choice):
                    template_name = next(t['name'] for t in templates if t['id'] == choice)
                    print(f"\n✓ 已选择模板: {template_name}")
                    return
                else:
                    print("模板切换失败，请重试")
            else:
                print("无效的模板ID，请重试")


def show_settings_menu():
    """
    显示设置菜单
    """
    while True:
        print("\n===== 设置 =====")
        print("1. 大纲生成模型")
        print("2. 内容生成模型")
        print("3. 最大API调用次数")
        print("4. 是否启用API")
        print("5. 是否启用百度搜索")
        print("6. PPT模板选择")
        print("7. 查看当前配置")
        print("8. 恢复默认设置")
        print("9. 返回主菜单")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            # 设置大纲生成模型
            model = input("请输入大纲生成模型: ").strip()
            if model:
                update_config("models.outline", model)
        elif choice == "2":
            # 设置内容生成模型
            model = input("请输入内容生成模型: ").strip()
            if model:
                update_config("models.content", model)
        elif choice == "3":
            # 设置最大API调用次数
            try:
                max_calls = int(input("请输入最大API调用次数: ").strip())
                if max_calls > 0:
                    update_config("max_api_calls", max_calls)
                else:
                    print("请输入大于0的数字")
            except ValueError:
                print("请输入有效的数字")
        elif choice == "4":
            # 设置是否启用API
            enable = input("是否启用API? (y/n): ").strip().lower()
            update_config("api.enable", enable in ['y', 'yes', '是'])
        elif choice == "5":
            # 设置是否启用百度搜索
            enable = input("是否启用百度搜索? (y/n): ").strip().lower()
            update_config("baidu_search.enable", enable in ['y', 'yes', '是'])
        elif choice == "6":
            # PPT模板选择
            show_template_menu()
        elif choice == "7":
            # 查看当前配置
            print_config()
        elif choice == "8":
            # 恢复默认设置
            reset_config()
        elif choice == "9":
            # 返回主菜单
            break
        else:
            print("输入无效，请重新选择")


def show_main_menu():
    """
    显示主菜单
    """
    while True:
        print("\n===== 智创易演 v2.0 =====")
        print("\n1. 开始生成PPT")
        print("2. 设置")
        print("3. 退出")
        
        choice = input("\n请选择: ").strip()
        
        if choice == "1":
            # 开始生成PPT
            main()
        elif choice == "2":
            # 进入设置菜单
            show_settings_menu()
        elif choice == "3":
            # 退出程序
            print("感谢使用，再见！")
            exit()
        else:
            print("输入无效，请重新选择")


def main(topic=None, num_slides=None):
    """
    主函数
    
    Args:
        topic: PPT主题（测试模式时使用）
        num_slides: 目标页数（测试模式时使用）
    """
    print("=== AI PPT Generator v1.0 ===")
    
    if topic and num_slides:
        # 测试模式
        topic, num_slides = test_mode(topic, num_slides)
    else:
        # 正常模式
        topic, num_slides = get_user_input()
    
    run(topic, num_slides)


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 3:
        # 测试模式
        topic = sys.argv[1]
        num_slides = int(sys.argv[2])
        main(topic, num_slides)
    else:
        # 正常模式 - 显示主菜单
        show_main_menu()
