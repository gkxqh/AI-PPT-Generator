import requests
from logger import info, error
from config import BAIDU_SEARCH_CONFIG

def need_search(topic: str) -> bool:
    """
    判断是否需要搜索
    
    Args:
        topic: PPT主题
    
    Returns:
        bool: 是否需要搜索
    """
    # 1. 时间敏感内容关键词
    time_keywords = ["最新", "2025", "2026", "2027", "发布", "上线", "推出", "上市", "更新", "版本"]
    
    # 2. 新实体类型关键词
    entity_keywords = ["动画", "游戏", "电影", "产品", "手机", "电脑", "软件", "应用", "服务", "平台"]
    
    # 3. 专业/冷门主题关键词
    professional_keywords = ["技术", "研究", "学术", "理论", "方法", "算法", "模型", "框架", "系统", "架构"]
    
    # 4. 特殊格式识别（如带书名号的内容）
    has_book_title = "《" in topic and "》" in topic
    
    # 5. 长度判断（较长的主题可能包含新实体）
    is_long_topic = len(topic) > 10
    
    # 6. 数字判断（包含年份、版本号等）
    contains_number = any(char.isdigit() for char in topic)
    
    # 综合判断
    if any(keyword in topic for keyword in time_keywords):
        return True
    
    if any(keyword in topic for keyword in entity_keywords):
        return True
    
    if any(keyword in topic for keyword in professional_keywords):
        return True
    
    if has_book_title:
        return True
    
    if is_long_topic and contains_number:
        return True
    
    return False


def search_baidu(query, api_key):
    """
    调用百度搜索API
    
    Args:
        query: 搜索查询词
        api_key: 百度API Key
    
    Returns:
        list: 搜索结果列表
    """
    try:
        # 构造搜索请求
        search_url = "https://qianfan.baidubce.com/v2/ai_search/web_search"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 按照官网要求构造请求体
        data = {
            "messages": [
                {
                    "content": query,
                    "role": "user"
                }
            ],
            "resource_type_filter": [
                {
                    "type": "web",
                    "top_k": 50
                },
                {
                    "type": "image",
                    "top_k": 30
                },
                {
                    "type": "video",
                    "top_k": 10
                }
            ],
            "edition": "standard",
            "search_filter": {
                "match": {
                    "site": []
                },
                "range": {
                    "page_time": {
                        "gte": "",
                        "lte": ""
                    }
                }
            },
            "search_recency_filter": "noTimeLimit"
        }
        
        info(f"发送百度搜索API请求: {query}")
        response = requests.post(search_url, headers=headers, json=data, timeout=15)
        
        info(f"百度搜索API响应状态码: {response.status_code}")
        
        # 打印完整响应内容，便于调试
        response_text = response.text
        info(f"百度搜索API响应内容: {response_text[:500]}...")  # 只打印前500个字符
        
        result = response.json()
        
        # 检查是否有错误
        if "code" in result and result["code"] != 0:
            error(f"百度搜索API错误: {result.get('message', '未知错误')}")
            return []
        
        # 处理返回结果
        search_results = []
        
        # 打印完整的返回结构，便于调试
        info(f"百度搜索API返回结构: {list(result.keys())}")
        
        # 检查返回结构
        if "search_results" in result:
            info(f"找到 search_results 字段，长度: {len(result['search_results'])}")
            for item in result["search_results"]:
                # 打印每个结果的结构
                info(f"搜索结果项结构: {list(item.keys())}")
                search_results.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "url": item.get("url", "")
                })
            info(f"成功获取 {len(search_results)} 条搜索结果")
        elif "data" in result:
            info(f"找到 data 字段，长度: {len(result['data'])}")
            # 兼容其他可能的返回格式
            for item in result["data"]:
                search_results.append({
                    "title": item.get("title", ""),
                    "content": item.get("desc", ""),
                    "url": item.get("url", "")
                })
            info(f"成功获取 {len(search_results)} 条搜索结果（兼容格式）")
        else:
            # 尝试其他可能的字段名
            for key in result:
                if isinstance(result[key], list):
                    info(f"找到列表字段: {key}，长度: {len(result[key])}")
                    # 尝试处理这个列表
                    for item in result[key]:
                        if isinstance(item, dict):
                            search_results.append({
                                "title": item.get("title", ""),
                                "content": item.get("content", item.get("desc", "")),
                                "url": item.get("url", "")
                            })
                    if search_results:
                        info(f"成功从 {key} 字段获取 {len(search_results)} 条搜索结果")
                        return search_results
            
            error(f"百度搜索API返回格式未知: {result}")
            return []
        
        return search_results
        
    except Exception as e:
        error(f"百度搜索API调用失败: {e}")
        import traceback
        error(f"详细错误信息: {traceback.format_exc()}")
        return []


def filter_results(results: list) -> list:
    """
    筛选搜索结果
    
    Args:
        results: 搜索结果列表
    
    Returns:
        list: 筛选后的搜索结果列表
    """
    filtered = []
    
    for result in results:
        # 1. 过滤空内容
        content = result.get('content', '').strip()
        if not content:
            continue
        
        # 2. 过滤过短内容（少于30字）
        if len(content) < 30:
            continue
        
        # 3. 计算信息密度（包含关键词数量）
        info_keywords = ['发布', '推出', '上线', '上市', '版本', '功能', '特点', '优势', '技术', '研究', '数据', '统计']
        info_density = sum(1 for keyword in info_keywords if keyword in content)
        
        # 4. 计算具体程度（包含数字的数量）
        specificity = sum(1 for char in content if char.isdigit())
        
        # 5. 计算综合得分
        score = len(content) * 0.1 + info_density * 2 + specificity * 1.5
        
        # 添加得分到结果中
        result['score'] = score
        filtered.append(result)
    
    # 6. 按得分排序，保留前10条
    filtered.sort(key=lambda x: x.get('score', 0), reverse=True)
    return filtered[:10]


def search_external(query: str) -> list:
    """
    搜索外部信息
    
    Args:
        query: 搜索查询词
    
    Returns:
        list: 搜索结果列表
    """
    info(f"正在搜索: {query}")
    
    # 从配置中获取百度API密钥
    if not BAIDU_SEARCH_CONFIG.get("enable", False):
        info("百度搜索API未启用")
        return []
    
    API_KEY = BAIDU_SEARCH_CONFIG.get("api_key", "")
    
    if not API_KEY:
        info("百度搜索API密钥未配置")
        return []
    
    # 调用百度搜索API
    results = search_baidu(query, API_KEY)
    
    if not results:
        # 如果API调用失败，直接返回空列表
        info("百度搜索API调用失败")
        return []
    
    info(f"百度搜索API调用成功，获取到 {len(results)} 条结果")
    return results


def build_context(docs: list) -> str:
    """
    构建上下文（信息压缩 + 结构化）
    
    Args:
        docs: 文档列表
    
    Returns:
        str: 构建好的上下文
    """
    context = ""
    total_length = 0
    max_docs = 5  # 最多保留5条高质量内容
    
    for i, doc in enumerate(docs[:max_docs]):
        title = doc.get('title', '')
        content = doc.get('content', '')
        
        # 1. 分割句子
        sentences = content.split('。')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # 2. 提取核心句子（最多2句）
        key_sentences = []
        for sentence in sentences:
            # 优先选择包含关键词的句子
            if any(keyword in sentence for keyword in ['发布', '推出', '上线', '功能', '特点', '技术', '数据']):
                key_sentences.append(sentence)
                if len(key_sentences) >= 2:
                    break
        
        # 如果没有找到关键词句子，选择前2句
        if not key_sentences:
            key_sentences = sentences[:2]
        
        # 3. 构建结构化内容
        doc_context = f"【参考资料{i+1}】\n"
        doc_context += f"标题: {title}\n"
        doc_context += "要点:\n"
        
        for j, sentence in enumerate(key_sentences):
            doc_context += f"* {sentence}。\n"
        
        doc_context += "\n"
        
        # 4. 控制总长度
        total_length += len(doc_context)
        if total_length > 1500:
            break
        
        context += doc_context
    
    return context


def retrieve_context(query: str) -> str:
    """
    检索上下文信息
    
    Args:
        query: 搜索查询词
    
    Returns:
        str: 上下文信息
    """
    # 1. 搜索外部信息
    docs = search_external(query)
    
    if not docs:
        return ""
    
    # 2. 筛选搜索结果
    filtered_docs = filter_results(docs)
    info(f"筛选后保留 {len(filtered_docs)} 条高质量参考资料")
    
    # 3. 构建上下文
    context = build_context(filtered_docs)
    
    # 4. 最终控制长度
    if len(context) > 1500:
        context = context[:1500]
        info("上下文长度超过1500，已截断")
    
    return context
