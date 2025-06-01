# -*- coding: utf-8 -*-
import os
import warnings
from autogen import ConversableAgent
from autogen import UserProxyAgent
import chardet
from config import OPENAI_API_KEY

warnings.filterwarnings('ignore')
model_coder = ConversableAgent(
    "model_coder",
    system_message="""
        You are a Product Manager. You have extensive experience in designing products
        and translating complex technical requirements into clear, user-centric scenarios.
    """,
    llm_config={
        "model": "gpt-4o",
        "temperature": 0.3,
        "api_key": OPENAI_API_KEY
    },
    human_input_mode="NEVER",
)
user_proxy = UserProxyAgent(
    name="user_proxy",
    system_message="A human admin.",  # 系统消息是用户给代理的角色
    code_execution_config={"last_n_messages": 2, "use_docker": False},
    human_input_mode="ALWAYS"
)


def get_responce(json_data, name):
    res = ''
    for item in json_data:
        try:
            if item.get('role') == name:
                res = res + item.get('content')
                print("Found code for", name, ":", item.get('content'))  # Add this line
        except:
            res = res + ""
    return res


def read_line(string, int):
    lines = string.split("\n")
    line = lines[int]
    return line


# 外部prompt读入函数
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()


def read_line(string, int):
    lines = string.split("\n")
    line = lines[int]
    return line


# prompt设置
req_temp = ("""
    According to the user’s task listed below: Task: "{task}".
    You should write down the use cases required by this
    task. Output format is: { 1: User can view the GUI. }
""")


raw_requirement_prompt = get_prompt_from_file("initial requirment.txt")


response = user_proxy.initiate_chat(model_coder,
                                    message=req_temp + "\n Task：\n" + raw_requirement_prompt)
# response2= user_proxy.initiate_chat(elysia, message="请根据以下需求生成PLC的ST代码"+"需求文件：\n"+raw_requirement_prompt)


model_coder.reset()

print("Chat history:", response.chat_history)
Use_case_design= get_responce(response.chat_history, 'user')
print("\nUse case design:", str(Use_case_design))
try:
    with open('AISD_design_req.txt', 'w', encoding='utf-8') as f:
        f.write(str(Use_case_design))

except Exception as e:
    print(f"Error writing to file: {e}")