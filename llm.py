import requests
import json
from config import MODEL_CONFIG, API_CONFIG
from logger import info, warning, error


def is_api_model(model_name: str) -> bool:
    """
    判断模型是否为API模型
    
    Args:
        model_name: 模型名称
    
    Returns:
        bool: 是否为API模型
    """
    # 本地模型列表
    local_models = ["qwen3:8b", "gemma3:12b"]
    
    # 如果模型名称包含冒号，通常是本地模型
    if ":" in model_name:
        return False
    
    # 如果模型名称在本地模型列表中，不是API模型
    if model_name in local_models:
        return False
    
    # 其他情况认为是API模型
    return True

def check_ollama_connection():
    """
    检查Ollama服务是否运行
    
    Returns:
        bool: Ollama服务是否可用
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def get_available_models():
    """
    获取Ollama中已安装的模型列表
    
    Returns:
        list: 模型名称列表
    """
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            return models
        return []
    except requests.RequestException:
        return []

def call_ollama(prompt, model="qwen3:8b", stream_callback=None):
    """
    调用本地Ollama API生成PPT结构
    
    Args:
        prompt: 输入的提示文本
        model: 使用的模型名称，默认为qwen3:8b
    
    Returns:
        str: LLM生成的文本响应
    """
    try:
        # 检查Ollama服务是否运行
        if not check_ollama_connection():
            error("无法连接到Ollama服务")
            error("请确保Ollama正在运行: ollama serve")
            return ""
        
        # 检查模型是否存在
        available_models = get_available_models()
        if model not in available_models:
            warning(f"模型 '{model}' 未找到")
            info(f"可用模型: {available_models}")
            # 尝试使用第一个可用模型
            if available_models:
                model = available_models[0]
                info(f"使用备用模型: {model}")
            else:
                error("没有可用的本地模型")
                return ""
        
        info(f"使用模型: {model}")
        
        # 构造请求体
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,  # 启用流式输出
            "temperature": 0.2,
            "num_predict": 2000  # 增加预测长度
        }
        
        # 发送POST请求到Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            stream=True,  # 启用流式响应
            timeout=120  # 增加超时时间
        )
        
        # 检查响应状态
        response.raise_for_status()
        
        # 处理流式响应
        full_response = ""
        for chunk in response.iter_lines():
            if chunk:
                try:
                    # 解析每个chunk的JSON
                    chunk_data = json.loads(chunk.decode('utf-8'))
                    # 获取生成的文本
                    if 'response' in chunk_data:
                        chunk_text = chunk_data['response']
                        full_response += chunk_text
                        # 逐字输出（这里可以根据需要调整输出频率）
                        if stream_callback:
                            stream_callback(chunk_text)
                        else:
                            print(chunk_text, end='', flush=True)
                    # 检查是否完成
                    if chunk_data.get('done', False):
                        break
                except json.JSONDecodeError:
                    pass
        
        # 输出换行
        print()
        
        return full_response
        
    except requests.exceptions.ConnectionError:
        error("无法连接到Ollama服务 (localhost:11434)")
        error("请确保Ollama正在运行: ollama serve")
        return ""
    except requests.exceptions.Timeout:
        error("请求超时，请检查Ollama服务状态")
        return ""
    except requests.exceptions.HTTPError as e:
        error(f"HTTP请求失败 - {e}")
        return ""
    except json.JSONDecodeError as e:
        error(f"JSON解析失败 - {e}")
        return ""
    except Exception as e:
        error(f"未知错误 - {e}")
        return ""

def call_api_model(prompt, model, stream_callback=None):
    """
    调用第三方API模型
    
    Args:
        prompt: 输入的提示文本
        model: 模型名称
    
    Returns:
        str: API返回的内容
    """
    if not API_CONFIG['enable']:
        error("API未启用")
        return ""
    
    try:
        # 智谱API的聊天接口
        url = f"{API_CONFIG['api_base']}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {API_CONFIG['api_key']}",
            "Content-Type": "application/json"
        }
        
        # 限制prompt长度，避免API拒绝
        max_prompt_length = 10000
        if len(prompt) > max_prompt_length:
            info(f"提示长度超过限制，截断到{max_prompt_length}字符")
            prompt = prompt[:max_prompt_length]
        
        data = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": stream_callback is not None,  # 如果提供了回调，则启用流式响应
            "max_tokens": 4096,  # 增加最大 tokens 数
            "temperature": 0.2  # 设置温度参数
        }
        
        info(f"发送API请求到: {url}")
        info(f"请求模型: {model}")
        info(f"请求长度: {len(prompt)} 字符")
        
        # 增加超时时间到120秒
        response = requests.post(url, headers=headers, json=data, timeout=120, stream=stream_callback is not None)
        response.raise_for_status()
        
        if stream_callback is not None:
            full_response = ""
            for chunk in response.iter_lines():
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    if chunk_str.startswith('data: '):
                        data_str = chunk_str[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            if 'choices' in data_json and len(data_json['choices']) > 0:
                                delta = data_json['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_response += content
                                    stream_callback(content)
                        except json.JSONDecodeError:
                            pass
            return full_response
        
        info(f"API响应状态码: {response.status_code}")
        
        # 解析响应
        result = response.json()
        info(f"API响应结构: {list(result.keys())}")
        
        # 处理响应数据
        if "choices" in result and result["choices"]:
            message = result["choices"][0]["message"]
            info(f"消息结构: {list(message.keys())}")
            
            # 优先使用content字段
            content = message.get("content", "")
            
            # 如果content为空，尝试使用reasoning_content
            if not content and "reasoning_content" in message:
                info("content字段为空，使用reasoning_content")
                content = message["reasoning_content"]
            
            info(f"获取到内容长度: {len(content)} 字符")
            
            # 验证内容是否有效
            if content:
                return content
            else:
                error("API返回内容为空")
                error(f"完整响应: {json.dumps(result, ensure_ascii=False)}")
                return ""
        else:
            error("API响应格式错误")
            error(f"完整响应: {json.dumps(result, ensure_ascii=False)}")
            return ""
        
    except requests.exceptions.Timeout:
        error("API请求超时，内容生成可能需要更长时间")
        return ""
    except requests.exceptions.HTTPError as e:
        error(f"API HTTP错误: {e}")
        error(f"响应内容: {response.text if 'response' in locals() else '无'}")
        return ""
    except requests.exceptions.ConnectionError:
        error("无法连接到API服务器")
        return ""
    except json.JSONDecodeError as e:
        error(f"JSON解析错误: {e}")
        error(f"响应内容: {response.text if 'response' in locals() else '无'}")
        return ""
    except Exception as e:
        error(f"API调用失败: {e}")
        import traceback
        error(f"详细错误: {traceback.format_exc()}")
        return ""

def call_llm(prompt, model="glm-5.1", stream_callback=None, on_fallback=None):
    """
    统一调用LLM函数
    
    Args:
        prompt: 输入的提示文本
        model: 使用的模型名称
        stream_callback: 流式输出的回调函数
        on_fallback: 当API失败降级到本地模型时的回调函数
    """
    info(f"[Model]: {model}")
    
    # 检查是否为API模型
    if is_api_model(model):
        info("尝试调用API模型...")
        try:
            result = call_api_model(prompt, model, stream_callback=stream_callback)
            if result:
                return result
        except Exception as e:
            error(f"API调用抛出异常: {e}")
        
        info("API调用失败，尝试使用本地模型...")
        if on_fallback:
            on_fallback()
    
    # 调用本地模型
    return call_ollama(prompt, model, stream_callback=stream_callback)

