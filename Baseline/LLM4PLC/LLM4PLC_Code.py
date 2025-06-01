# -*- coding: utf-8 -*-
from openai import OpenAI
import sys
from pathlib import Path
import chardet
import os
import re
import io
import warnings

# 设置标准输出为 UTF-8 编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')

# Add project root to Python path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

# Make sure config file exists or provide default values
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

# --- Helper Function ---
def get_prompt_from_file(file_path):
    """Reads content from a file, detecting encoding."""
    try:
        with open(file_path, 'rb') as file:
            raw_data = file.read()
            if not raw_data:
                print(f"[WARN] File is empty: {file_path}")
                return ""
            result = chardet.detect(raw_data)
            encoding = result['encoding'] or 'utf-8'
        with open(file_path, 'r', encoding=encoding, errors='replace') as file:
            return file.read()
    except FileNotFoundError:
        print(f"[WARN] File not found: {file_path}. Returning empty string.")
        return ""
    except Exception as e:
        print(f"[ERROR] Failed to read file {file_path}: {e}")
        return ""

# --- Core LLM Call Function ---
def call_llm(sys_msg: str, user_msg: str) -> str:
    """Calls the LLM, prints interaction, saves full response, and extracts/saves SCL code."""
    client = OpenAI(api_key=openai_api_key, base_url=openai_base_url)

    print(f"\n[CALL LLM]")
    print(f"System: {sys_msg[:500]}...")  # Truncate long system prompt
    print(f"User:   {user_msg}")

    try:
        completion = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user",   "content": user_msg}
            ]
        )
        response_content = completion.choices[0].message.content
        print(f"Assistant: {response_content}\n")

        # 保存完整输出
        with open("LLM4PLC_CODE.txt", "w", encoding="utf-8") as f:
            f.write(response_content)
        print("[INFO] Full LLM response saved to LLM4PLC_CODE.txt")

        # 提取 SCL 代码块
        match = re.search(r'START_SCL(.*?)END_SCL', response_content, re.DOTALL | re.IGNORECASE)
        if match and match.group(1).strip():
            extracted_code = match.group(1).strip()
            with open("LLM4PLC_Code.scl", "w", encoding="utf-8") as f:
                f.write(extracted_code)
            print("[INFO] Extracted SCL code saved to LLM4PLC_Code.scl")
        else:
            print("[INFO] No SCL code found between START_SCL/END_SCL tags.")

    except Exception as e:
        print(f"[ERROR] Failed to call LLM or process response: {e}")
        response_content = f"Error: {e}"

    return response_content

# --- Main Execution Block ---
if __name__ == "__main__":
    print("[INFO] Loading prompts...")
    plan_prompt = get_prompt_from_file("LLM4PLC_PLAN.txt")
    requirement_prompt = get_prompt_from_file("requirment.txt")

    sys_prompt = f"""
YOU ARE A HELPFUL ASSISTANT TASKED WITH SUCCESSIVE PHASES TO HELP AN OPERATOR PROGRAM AND MAINTAIN CODE FOR AN INDUSTRIAL PLC THROUGH THE SCL LANGUAGE.
[TASK_DESCRIPTION_START]
YOU WILL TRANSFORM THE CODING PLAN INTO SCL CODE.
IMPERATIVE: DO NOT OMIT OR SUMMARIZE ANYTHING FROM THE PLAN
IMPERATIVE: AVOID SYNTAX ERRORS
IMPERATIVE: AIM FOR READABILITY/MAINTAINABILITY
IMPERATIVE: AIM FOR EFFICIENCY
IMPERATIVE: AIM FOR COMPLETENESS, STICK TO THE PLAN
IMPORTANT: START YOUR CODE WITH "START_SCL" AND END THEM WITH "END_SCL"
[TASK_DESCRIPTION_END]


TASK: TRANSFORM THE PLAN INTO SCL CODE.
ORIGINAL REQUIREMENT:
{requirement_prompt}
CURRENT PLAN:
{plan_prompt}
"""

    # 不再加载或打印上一次生成的 SCL 代码
    # last_code = load_last_output()
    # if last_code:
    #     ...

    print("=== LLM SCL Code Generation ===")
    print("Enter your request (e.g., 'Generate the code based on the plan', 'Refine the previous code', or type 'exit'/'quit'):")

    while True:
        try:
            user_input = input("User > ").strip()
            if not user_input:
                print("[INFO] No input provided. Using default: 'Generate the SCL code based on the current plan.'")
                user_input = "Generate the SCL code based on the current plan."
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Exiting.")
            break

        call_llm(sys_prompt, user_input)
