# -*- coding: utf-8 -*-
from openai import OpenAI
import sys
from pathlib import Path
import chardet
import os
from config import chat_model, openai_api_key, openai_base_url
# Add project root to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))
import io
import warnings
# 设置标准输出为 UTF编码
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()

def call_llm(sys_msg: str, user_msg: str) -> str:
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_base_url,
    )

    print(f"\n[CALL LLM]")
    print(f"System: {sys_msg}")
    print(f"User:   {user_msg}")

    completion = client.chat.completions.create(
        model=chat_model,
        messages=[
            {"role": "system", "content": sys_msg},
            {"role": "user",   "content": user_msg}
        ]
    )

    response_content = completion.choices[0].message.content
    print(f"Assistant: {response_content}\n")

    # Save last output to LLM4PLC_PLAN.txt
    try:
        with open("LLM4PLC_PLAN.txt", "w", encoding="utf-8") as f:
            f.write(response_content)
    except Exception as e:
        print(f"[WARN] Failed to save last output: {e}")

    return response_content

def load_last_output(file_path="LLM4PLC_PLAN.txt") -> str:
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"[WARN] Failed to read last output: {e}")
    return ""

mbd_prompt = get_prompt_from_file("mbd_prompt.txt")
original_requirement = get_prompt_from_file("requirment.txt")
if __name__ == "__main__":
    sys_prompt = """
        YOU ARE A HELPFUL ASSISTANT TASKED WITH SUCCESSIVE PHASES TO HELP AN OPERATOR PROGRAM AND MAINTAIN CODE FOR AN INDUSTRIAL PLC THROUGH THE SCL LANGUAGE AND SMV VERIFICATION TOOLCHAINS.
        PHASE: PLANNING
        THE USER WILL PROVIDE GIVEN REQUIREMENTS AND SPECIFICATIONS. YOUR FIRST TASK IS TO PLAN THE COMPONENTS OF THE PROGRAM IN SCL BEFORE PROPOSING THE ACTUAL CODE IMPLEMENTATION. THE USER WILL PROVIDE A NATURAL LANGUAGE DESCRIPTION OF BOTH THE PLANT AND THE NEEDED OPERATION. YOU WILL PROPOSE A DETAILED PLAN FOR THE CODE, INCLUDING FUNCTION AND BLOCK DECLARATIONS AS WELL AS THEIR SIGNATURES. YOU CAN ASK THE USER QUESTIONS.
        IMPERATIVE: DO NOT MAKE ANY ASSUMPTIONS.
        IMPERATIVE: DO NOT MAKE ANY ADDITIONS, MODIFICATIONS, OR REMOVAL OF NEEDED INFORMATION.
        IMPORTANT: YOU MAY ASK QUESTIONS IF THE GIVEN SPECIFICATIONS ARE AMBIGUOUS.
        IMPERATIVE: KEEP IN MIND THE PLC SCAN CYCLE: THE CODE WILL EXECUTE IN CYCLES AS DEFINED IN TYPICAL STRUCTURED TEXT LANGUAGES.
        IMPERATIVE: WHEN CHANGING VARIABLES OVER TIME, YOU NEED TO KEEP TRACK OF THE STATE THROUGH DIFFERENT CYCLES AND STOP WHEN THE NEEDED STATE IS REACHED.
        IMPORTANT: START YOUR PLAN WITH "START_PLAN" AND END IT WITH "END_PLAN"
        IMPORTANT: IF YOU ARE ASKING QUESTIONS, START YOUR QUESTIONS WITH "START_QUESTION" AND END THEM WITH "END_QUESTION"
        IMPORTANT: PLAN ACCORDING TO A FINITE STATE MACHINE DESIGN. EXPLAIN EACH STATE AND OUTPUTS CLEARLY.
        The PLAN FORMAT FOR THE CODE IS AS FOLLOWS:
    """ + mbd_prompt + "\nOriginal Requirement: " + original_requirement

    print("=== LLM Chat REPL ===")
    print("Enter your request (e.g., 'Generate the plan based on the original requirement', or type 'exit'/'quit'):")

    while True:
        try:
            user_input = input("User > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        call_llm(sys_prompt, user_input)
