import ollama

chatoutput = ollama.chat(model='deepseek-r1:7b', 
            messages=[{'role': 'user', 'content': '天为什么是蓝色的?'}]
)


print(chatoutput)

print("generate plan")
# generate 方法

chatoutput = ollama.generate(model='deepseek-r1:7b', prompt='天为什么是蓝色的?')

print(chatoutput)

# show 方法

output = ollama.show(model='deepseek-r1:7b')

print(" show 方法输出 \n",output)

chatoutput = ollama.create(model='deepseek-r1:7b', from_='deepseek-r1:7b', system="You are Mario from Super Mario Bros.")

print("create 方法输出 \n",chatoutput)

# embed 方法 
chatoutput = ollama.embed(model='deepseek-r1:7b', input='The sky is blue because of rayleigh scattering')

print("embed 方法输出 \n",chatoutput)

model = 'does-not-yet-exist'

# 错误处理
try:
    response = ollama.chat(model)
except ollama.ResponseError as e:
    print('Error:', e.error)
    if e.status_code == 404:
        ollama.pull(model)