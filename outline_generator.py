from llm import call_llm
import json
from logger import info, error
from config import get_config


def build_outline_prompt(topic, num_slides):
    """
    构建大纲生成的 prompt
    
    Args:
        topic: PPT主题
        num_slides: 目标页数
    
    Returns:
        str: 构建好的prompt
    """
    content_count = num_slides - 2 if num_slides > 2 else 0
    
    prompt = f"""
你是一个专业的PPT结构设计助手。
请根据主题生成PPT结构大纲。

【重要规则】
1. 只输出JSON对象，不要有任何其他文字或Markdown标记
2. 不要使用 ```json 或 ``` 等标记
3. 直接输出JSON，从 {{ 开始，到 }} 结束
4. 使用双引号，不要使用单引号

【页数要求】
- 总页数必须为 {num_slides} 页
- 第1页：type="intro"（引言）
- 中间 {content_count} 页：type="content"（内容页）
- 最后一页：type="summary"（总结）

【输出格式】
{{
  "title": "{topic}",
  "slides": [
    {{ "title": "引言标题", "type": "intro" }},
    {{ "title": "内容标题1", "type": "content" }},
    {{ "title": "内容标题2", "type": "content" }},
    {{ "title": "总结标题", "type": "summary" }}
  ]
}}

现在请为主题"{topic}"生成大纲，直接输出JSON：
"""
    return prompt


def parse_json(result):
    """
    解析LLM返回的JSON
    
    Args:
        result: LLM返回的文本
    
    Returns:
        dict: 解析后的JSON数据
    """
    import re
    
    try:
        # 方法1: 尝试提取Markdown代码块中的JSON
        code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
        code_matches = re.findall(code_block_pattern, result)
        
        for code_content in code_matches:
            code_content = code_content.strip()
            if code_content.startswith('{') and code_content.endswith('}'):
                try:
                    return json.loads(code_content)
                except:
                    continue
        
        # 方法2: 尝试提取JSON对象
        # 找到最后一个完整的JSON对象（从第一个{到最后一个}）
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_candidate = result[start_idx:end_idx + 1]
            try:
                return json.loads(json_candidate)
            except:
                pass
        
        # 方法3: 使用正则表达式匹配
        json_pattern = r'\{[\s\S]*"slides"[\s\S]*\}'
        json_match = re.search(json_pattern, result)
        if json_match:
            try:
                return json.loads(json_match.group(0))
            except:
                pass
        
        error("未找到有效的JSON内容")
        error(f"原始响应内容（前500字符）: {result[:500]}")
        return None
        
    except json.JSONDecodeError as e:
        error(f"JSON解析错误: {e}")
        error(f"原始响应内容（前500字符）: {result[:500]}")
        return None
    except Exception as e:
        error(f"解析错误: {e}")
        return None


def generate_outline(topic, num_slides, stream_callback=None, on_fallback=None):
    """
    生成PPT大纲
    
    Args:
        topic: PPT主题
        num_slides: 目标页数
        stream_callback: 流式输出的回调函数
        on_fallback: 降级提示的回调函数
    
    Returns:
        dict: 大纲数据
    """
    prompt = build_outline_prompt(topic, num_slides)
    # 动态获取最新配置
    config = get_config()
    model = config['models'].get('outline', 'glm-5.1')
    result = call_llm(prompt, model=model, stream_callback=stream_callback, on_fallback=on_fallback)
    outline = parse_json(result)
    if outline and "slides" in outline:
        info(f"大纲生成成功，共 {len(outline['slides'])} 页")
    return outline
