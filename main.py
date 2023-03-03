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
                    {"role": "system", "content": "You are a helpful assistant."},
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



def seed():
    print("hello world")
    return gr.update(default=random.randint(1, 100000000000))


# 创建一个UI界面，并指定输入和输出的类型
question_box = gr.inputs.Textbox(label="Question") # 创建一个输入框组件，并赋值给question_box变量，方便后续操作
user_id_box = gr.inputs.Textbox(label="UserId",default=lambda:str(time.time())) # 创建一个输入框组件，并赋值给question_box变量，方便后续操作
answer_boxes = []
for i in range(0,10):
    answer_boxes.append(gr.outputs.Textbox(label="Answer"+str(i))) # 创建一个输出框组件，并赋值给answer_box变量，方便后续操作

interface = gr.Interface(
    fn=ask_openai,
    inputs=[question_box,user_id_box], 
    outputs=answer_boxes,
    share=True, # 启用分享功能，并生成公开链接 
    analytics_enabled=True # 启用分析功能，并记录每个用户的输入和输出数据 
)

with interface:
    user_id_box.set_event_trigger("load", seed, None, None)


# 启动界面，并在浏览器中查看效果
interface.launch()