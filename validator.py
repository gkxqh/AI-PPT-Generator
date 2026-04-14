def validate_slides(slides):
    """
    轻量级校验幻灯片内容
    
    Args:
        slides: 幻灯片列表
    
    Returns:
        list: 校验后的幻灯片列表
    """
    fixed = []
    
    for slide in slides:
        # 确保slide是字典
        if not isinstance(slide, dict):
            slide = {}
        
        # 确保title存在
        if not slide.get("title"):
            slide["title"] = "未命名页面"
        
        # 确保bullets存在且是列表
        if not slide.get("bullets"):
            slide["bullets"] = ["内容生成失败"]
        elif not isinstance(slide["bullets"], list):
            slide["bullets"] = ["内容生成失败"]
        
        # 确保content存在
        if not slide.get("content"):
            slide["content"] = "内容生成失败"
        
        fixed.append(slide)
    
    return fixed
