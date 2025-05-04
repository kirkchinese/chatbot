from ollama import chat

stream = chat(
    model='deepseek-r1:7b',
    messages=[{'role': 'user', 'content': '讲一个笑话给我吧！'}],
    stream=True,
)

# 逐块打印响应内容
for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)