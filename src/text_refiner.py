import requests
import json

def refine_text(api_key: str, text: str) -> str:
    """
    使用DeepSeek API进行文本润色
    :param api_key: DeepSeek API密钥
    :param text: 需要润色的原始文本
    :return: 润色后的文本
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一个专业的文本润色助手，请用更优雅的中文表达改写用户提供的文本，保持原意不变。"
            },
            {
                "role": "user", 
                "content": text
            }
        ],
        "temperature": 0.3,
        "max_tokens": 2000
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}")
        return None
    except KeyError:
        print("响应格式解析错误")
        return None

if __name__ == "__main__":
    # 示例使用
    API_KEY = "sk-862159fd441345c0ae51a129101d2ebe"  # 替换为实际密钥
    input_text = "这个产品很好用，但价格有点贵。"
    
    refined = refine_text(API_KEY, input_text)
    print("\n润色结果：\n" + refined if refined else "润色失败")
