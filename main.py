import os
import openai
import gradio as gr
import time
import random
import configparser


# 创建一个ConfigParser对象
config = configparser.ConfigParser()

# 读取一个INI文件
config.read("config.ini")

organization=config.get("main", "organization")
api_key=config.get("main", "api_key")
model=config.get("main", "model")
print(organization,api_key,model)



# 设置组织ID和API密钥
openai.organization = organization
openai.api_key = api_key

# 选择一个gpt模型
model = model

# 定义一个字典，用来保存每个用户的聊天上下文
contexts = {}

# 定义一个函数，接收一个问题和一个用户ID作为输入，并返回openai的答案作为输出
def ask_openai(question, user_id):
    global contexts # 使用全局变量contexts
    print(question,user_id)
    if user_id not in contexts: # 如果用户ID不在字典中，则初始化一个空值
        contexts[user_id] = None 
    context = contexts[user_id] # 根据用户ID获取对应的聊天上下文
    if context==None:
        context={
                "messages":[
                    ]
        }
    context["messages"].append(
            {"role": "user", "content": question}
            )
    print(context)
    response = openai.ChatCompletion.create(
        model=model,
        messages=context["messages"],
        temperature=0,
    )
    print(response)
    answer = response["choices"][0]["message"]["content"]
    
    context["messages"].append(response["choices"][0]["message"])
    
    context["messages"]= context["messages"][-6:]

    contexts[user_id] = context # 将更新后的聊天上下文保存到字典中
    answers=list(map(lambda m:m["content"],reversed(context["messages"])))
    for i in range(len(answers),10):
        answers.append("")
    print(answers)
    gr.update(default=random.randint(1, 100000000000))
    return answers[:10]






with gr.Blocks() as interface:
    gr.Markdown(
"""
# Hello World!
Start typing below to see the output.
```python
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr
```
""")
    with gr.Row():
        user_id_box = gr.Textbox(label="UserId",value=lambda:str(time.time())) # 创建一个输入框组件，并赋值给question_box变量，方便后续操作
        new_session_btn = gr.Button(value="NewSession")

    with gr.Row():
        # 创建一个UI界面，并指定输入和输出的类型
        question_box = gr.Textbox(label="Question") # 创建一个输入框组件，并赋值给question_box变量，方便后续操作
        submit_btn = gr.Button(value="Submit")
    gr.Markdown(
        """
        # Output
        """)
    
    answer_boxes = []
    for i in range(0,10):
        with gr.Row():
            answer_boxes.append(gr.Markdown(label="Answer"+str(i))) # 创建一个输出框组件，并赋值给answer_box变量，方便后续操作
    
    def new_session():
        ret=str(time.time())
        #, list(map(lambda a:"",range(0,len(answer_boxes))))
        return ret
                
    new_session_btn.click(fn=new_session,outputs=[user_id_box])
    
    submit_btn.click(fn=ask_openai,inputs=[question_box,user_id_box],outputs=answer_boxes)
    question_box.submit(fn=ask_openai,inputs=[question_box,user_id_box],outputs=answer_boxes)
    


# 启动界面，并在浏览器中查看效果
interface.launch()
