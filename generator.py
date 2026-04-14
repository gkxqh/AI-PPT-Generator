from llm import call_llm
import json
from logger import info, error
from config import get_config


def generate_full_ppt(topic, outline, context, stream_callback=None, on_fallback=None):
    """
    一次性生成完整PPT内容
    
    Args:
        topic: PPT主题
        outline: PPT大纲
        context: 检索到的上下文信息
    
    Returns:
        list: 完整的slides列表
    """
    info("正在生成PPT内容...")
    
    # 构建完整的prompt
    slides_outline = "\n".join([f"- {slide.get('title', '')} (type: {slide.get('type', 'content')})" for slide in outline.get('slides', [])])
    
    prompt = f"""
你是一个专业的PPT内容生成助手。
请根据以下信息生成完整的PPT内容。

【重要规则】
1. 只输出严格合法的JSON数组，不要有任何其他文字、说明或前言后语
2. 绝对不能省略逗号！确保JSON对象之间、键值对之间、数组元素之间都有正确的逗号分隔
3. 文本内容中如果包含双引号（"）或反斜杠（\），必须进行转义，例如：`\"` 和 `\\`
4. 不要使用 ```json 或 ``` 等Markdown标记，直接从 [ 开始，到 ] 结束
5. 所有属性名和字符串值必须使用双引号 (")，不能使用单引号
6. 严禁在 JSON 中使用任何注释 (// 或 /*)

【PPT主题】
{topic}

【PPT大纲】
{slides_outline}

【参考资料】
{context if context else "无"}

【每页必需字段】
- title: 页面标题（字符串）
- type: 页面类型（"intro"/"content"/"summary"）
- bullets: 要点列表（字符串数组，3-5个要点）
- content: 详细内容（字符串，50-100字）
- key_message: 关键信息（字符串，简短有力）

【图表使用规则】
图表是可选的，只在以下场景使用：
1. 数据对比场景（如销量对比、性能对比）→ 使用柱状图 (bar)
2. 趋势变化场景（如增长趋势、发展历程）→ 使用折线图 (line)
3. 占比分布场景（如市场份额、组成比例）→ 使用饼图 (pie)

以下场景不需要图表：
- 概念介绍、理论说明
- 纯文字描述
- 总结页
- 缺乏具体数据

【图表字段格式】（仅在需要时添加）
- chart: 图表配置对象（可选）
  - type: 图表类型 ("bar"/"line"/"pie")
  - title: 图表标题
  - categories: 类别数组（如 ["2020", "2021", "2022"]）
  - series: 数据系列数组
    - name: 系列名称
    - values: 数值数组

【输出示例】
[
    {{
        "title": "销售数据分析",
        "type": "content",
        "bullets": ["2023年销售额增长20%", "市场占有率提升至35%"],
        "content": "销售数据显示持续增长态势...",
        "key_message": "业绩稳步提升",
        "chart": {{
            "type": "bar",
            "title": "季度销售额对比",
            "categories": ["Q1", "Q2", "Q3", "Q4"],
            "series": [
                {{"name": "2023年", "values": [120, 150, 180, 200]}}
            ]
        }}
    }},
    {{
        "title": "产品介绍",
        "type": "content",
        "bullets": ["功能强大", "易于使用"],
        "content": "产品具有多种优势...",
        "key_message": "领先的产品体验"
    }}
]

现在请直接输出JSON数组：
"""
    
    # 调用LLM生成内容
    # 动态获取最新配置
    config = get_config()
    model = config['models'].get('content', 'glm-5.1')
    result = call_llm(prompt, model=model, stream_callback=stream_callback, on_fallback=on_fallback)
    
    # 解析JSON结果
    try:
        # 清理和提取JSON
        json_str = extract_json(result)
        
        if json_str:
            # 尝试做一些基本的非法字符清理（比如大模型偶尔会在结尾少输出括号或有换行问题）
            json_str = json_str.strip()
            slides = json.loads(json_str)
            info(f"内容生成成功，共 {len(slides)} 页")
            return slides
        else:
            error("未找到有效的JSON内容")
            # 打印原始响应以便调试
            error(f"原始响应内容（前500字符）: {result[:500]}")
            return []
    except json.JSONDecodeError as e:
        error(f"JSON解析错误: {e}")
        error(f"原始响应内容（前500字符）: {result[:500]}")
        return []
    except Exception as e:
        error(f"解析错误: {e}")
        return []


def extract_json(text):
    """
    从文本中提取JSON内容
    支持多种格式：
    1. 纯JSON数组
    2. Markdown代码块中的JSON
    3. 混合文本中的JSON
    
    Args:
        text: 包含JSON的文本
    
    Returns:
        str: 提取出的JSON字符串，如果未找到则返回None
    """
    import re
    
    # 方法1: 尝试提取Markdown代码块中的JSON
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    code_matches = re.findall(code_block_pattern, text)
    
    for code_content in code_matches:
        code_content = code_content.strip()
        # 检查是否是JSON数组
        if code_content.startswith('[') and code_content.endswith(']'):
            try:
                # 验证是否是有效JSON
                json.loads(code_content)
                return code_content
            except:
                continue
    
    # 方法2: 尝试提取纯JSON数组
    json_array_pattern = r'\[\s*\{[\s\S]*\}\s*\]'
    json_match = re.search(json_array_pattern, text)
    if json_match:
        return json_match.group(0)
    
    # 方法3: 尝试查找第一个 [ 到最后一个 ] 之间的内容
    start_idx = text.find('[')
    end_idx = text.rfind(']')
    
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        json_candidate = text[start_idx:end_idx + 1]
        try:
            # 验证是否是有效JSON
            json.loads(json_candidate)
            return json_candidate
        except:
            pass
    
    return None
