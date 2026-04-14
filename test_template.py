"""
测试模板系统
"""
from template_manager import (
    list_templates, 
    set_current_template, 
    get_current_template,
    print_templates
)
from ppt_generator import generate_ppt
from logger import info


def test_template_system():
    """
    测试模板系统功能
    """
    print("\n" + "=" * 60)
    print("测试模板系统")
    print("=" * 60)
    
    # 1. 列出所有模板
    print("\n1. 列出所有模板:")
    templates = list_templates()
    for t in templates:
        current = " [当前]" if t['is_current'] else ""
        print(f"   - {t['id']}: {t['name']}{current}")
        print(f"     描述: {t['description']}")
    
    # 2. 测试切换模板
    print("\n2. 测试切换模板:")
    test_template_ids = ["business", "tech", "creative", "dark"]
    
    for template_id in test_template_ids:
        print(f"\n切换到模板: {template_id}")
        if set_current_template(template_id):
            current = get_current_template()
            print(f"[OK] 当前模板: {current['name']}")
        else:
            print(f"[FAIL] 切换失败")
    
    # 3. 切换回默认模板
    print("\n3. 切换回默认模板:")
    set_current_template("default")
    current = get_current_template()
    print(f"[OK] 当前模板: {current['name']}")
    
    print("\n" + "=" * 60)
    print("模板系统测试完成")
    print("=" * 60)


def test_ppt_generation_with_templates():
    """
    测试使用不同模板生成PPT
    """
    print("\n" + "=" * 60)
    print("测试PPT生成（使用模板）")
    print("=" * 60)
    
    # 测试数据
    test_data = {
        "title": "模板测试演示文稿",
        "slides": [
            {
                "title": "引言",
                "type": "intro",
                "bullets": ["这是第一个要点", "这是第二个要点", "这是第三个要点"],
                "content": "这是详细内容的描述，用于展示模板对内容样式的处理效果。",
                "key_message": "这是关键信息，会以强调样式显示"
            },
            {
                "title": "主要内容",
                "type": "content",
                "bullets": ["要点一：数据分析", "要点二：可视化呈现", "要点三：结果解读"],
                "content": "本页展示主要内容页面的模板效果，包含项目符号、详细内容和关键信息。",
                "key_message": "核心结论：模板系统运行正常"
            },
            {
                "title": "总结",
                "type": "summary",
                "bullets": ["总结要点一", "总结要点二"],
                "content": "这是总结页面的内容，用于回顾全文重点。",
                "key_message": "感谢观看"
            }
        ]
    }
    
    # 测试不同模板
    template_ids = ["default", "business", "tech", "creative", "dark", "nature", "academic"]
    
    for template_id in template_ids:
        print(f"\n使用模板 '{template_id}' 生成PPT...")
        
        from template_manager import get_template
        template = get_template(template_id)
        
        if template:
            output_file = f"test_template_{template_id}.pptx"
            success = generate_ppt(test_data, output_file, template)
            
            if success:
                print(f"[OK] 成功生成: {output_file}")
            else:
                print(f"[FAIL] 生成失败: {output_file}")
        else:
            print(f"[FAIL] 模板不存在: {template_id}")
    
    print("\n" + "=" * 60)
    print("PPT生成测试完成")
    print("=" * 60)


if __name__ == "__main__":
    # 测试模板系统
    test_template_system()
    
    # 测试PPT生成（可选）
    print("\n是否测试PPT生成？(y/n): ", end="")
    choice = input().strip().lower()
    if choice in ['y', 'yes', '是']:
        test_ppt_generation_with_templates()
