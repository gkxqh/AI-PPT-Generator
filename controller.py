from outline_generator import generate_outline
from retrieval import need_search, retrieve_context
from generator import generate_full_ppt
from validator import validate_slides
from ppt_generator import generate_ppt
from logger import info, error
from template_manager import get_current_template
from progress import ProgressBar
import datetime


def run(topic: str, num_slides: int):
    """
    主流程控制
    
    Args:
        topic: PPT主题
        num_slides: 目标页数
    """
    # 初始化进度条
    progress = ProgressBar(total_steps=5, desc=f"PPT Generation: {topic}")
    progress.start()
    
    print(f"\n  Topic: {topic}")
    print(f"  Target: {num_slides} slides")
    print()
    
    # 1. 生成大纲
    progress.update(1, "running", "Generating outline...")
    outline = generate_outline(topic, num_slides)
    
    if not outline or "slides" not in outline:
        progress.error(1, "Outline generation failed")
        return
    
    progress.update(1, "done", f"Generated {len(outline['slides'])} slides outline")
    
    # 显示大纲内容
    print("\n" + "-" * 60)
    print("  PPT Outline Details:")
    print("-" * 60)
    print(f"  Title: {outline.get('title', topic)}")
    print(f"  Total: {len(outline['slides'])} slides\n")
    
    for i, slide in enumerate(outline['slides'], 1):
        slide_title = slide.get('title', f"Slide {i}")
        slide_type = slide.get('type', 'content')
        type_display = {
            'intro': 'Intro',
            'content': 'Content',
            'summary': 'Summary'
        }.get(slide_type, 'Content')
        print(f"  [{i:2d}] [{type_display:7s}] {slide_title}")
    
    print("-" * 60 + "\n")

    # 1.5 大纲人机协同确认
    print("=" * 60)
    print("  大纲生成完毕！您可以检查上方的目录结构。")
    print("  [y] 直接继续生成内容")
    print("  [n] 取消生成任务")
    print("=" * 60)
    while True:
        user_confirm = input("是否继续？(y/n) [默认y]: ").strip().lower()
        if not user_confirm or user_confirm == 'y':
            print("  -> 用户确认，继续生成 PPT...\n")
            break
        elif user_confirm == 'n':
            progress.error(1, "用户取消了生成任务")
            return
        else:
            print("  -> 输入无效，请输入 y 或 n。")
    
    
    # 2. 可选检索（非阻断）
    context = ""
    progress.update(2, "running", "Checking if search is needed...")
    
    if need_search(topic):
        progress.update(2, "running", "Searching for reference materials...")
        context = retrieve_context(topic)
        if context:
            progress.update(2, "done", "Reference materials retrieved")
        else:
            progress.update(2, "done", "No references found, using model knowledge")
    else:
        progress.update(2, "done", "Search skipped (not needed for this topic)")
    
    # 3. 生成内容
    progress.update(3, "running", "Generating slide content...")
    slides = generate_full_ppt(topic, outline, context)
    
    if not slides:
        progress.error(3, "Content generation failed")
        return
    
    progress.update(3, "done", f"Generated content for {len(slides)} slides")
    
    # 4. 校验内容
    progress.update(4, "running", "Validating content...")
    validated_slides = validate_slides(slides)
    progress.update(4, "done", "Content validation completed")
    
    # 5. 生成PPT
    progress.update(5, "running", "Creating PPT file...")
    
    # 获取当前模板
    current_template = get_current_template()
    print(f"\n  Using template: {current_template.get('name', 'Default')}\n")
    
    ppt_data = {
        "title": topic,
        "slides": validated_slides
    }
    
    # 生成文件名
    current_time = datetime.datetime.now().strftime("%Y%m%d%H%M")
    safe_topic = topic.replace(" ", "_").replace("\n", "_").replace("/", "_").replace("\\", "_")
    output_filename = f"{safe_topic}_{current_time}.pptx"
    
    success_status = generate_ppt(ppt_data, output_filename, current_template)
    
    if success_status:
        progress.complete(f"PPT generated successfully: {output_filename}")
    else:
        progress.error(5, "PPT file generation failed")
