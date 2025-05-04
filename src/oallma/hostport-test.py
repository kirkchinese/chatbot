from ollama import Client
import ollama
list1 = ollama.list()
print(list1.models)

type0 = type(list1.models)
client = Client(
    host='http://localhost:11434',
    headers={'x-some-header': 'some-value'}
)

response = client.chat(model='deepseek-r1:7b', messages=[
    {
        'role': 'user',
        'content': '你是谁?',
    },
])
print(response['message']['content'])