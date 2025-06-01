# -*- coding: utf-8 -*-
import warnings
import os
import chardet
import glob
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, ServiceContext, StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core import Settings
import sys
import io
import re
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

folder_path = 'ST_Grammar'
# 使用glob模式匹配文件夹中的所有md文件
md_files = glob.glob(os.path.join(folder_path, '*.md'))
# 使用SimpleDirectoryReader读取所有文件
documents = SimpleDirectoryReader(input_files=md_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))

# 设置全局配置
Settings.llm = OpenAI(model="gpt-4o", temperature=0.1)
Settings.chunk_size = 512  # 根据需要设置
Settings.chunk_overlap = 20  # 根据需要设置
def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="ST_Grammar_index",
):
    # 创建句子窗口的 node parser
    node_parser = SentenceWindowNodeParser(
        window_size=sentence_window_size,
        window_metadata_key="window",
        original_text_metadata_key="original_text",
    )

    if not os.path.exists(save_dir):
        sentence_index = VectorStoreIndex.from_documents(
            documents, embed_model=embed_model, node_parser=node_parser
        )
        sentence_index.storage_context.persist(persist_dir=save_dir)
    else:
        storage_context = StorageContext.from_defaults(persist_dir=save_dir)
        sentence_index = load_index_from_storage(
            storage_context,
            embed_model=embed_model,
            node_parser=node_parser,
        )

    return sentence_index

def get_sentence_window_query_engine(
        sentence_index, similarity_top_k=6, rerank_top_n=2
):
    # define postprocessors
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )

    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
    )
    return sentence_window_engine

index = build_sentence_window_index(
    [document],
    save_dir="ST_Grammar_index",
)
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)

# 定义查询
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()

original_requirement = get_prompt_from_file("requirment.txt")
usecase_prompt = get_prompt_from_file("R2IL_design_req.txt")
grammar_prompt = get_prompt_from_file("st_rules.txt")
code_prompt = get_prompt_from_file("Modify_Code.txt")
# 改进后的提示词设计
query_str = ("""
            You are an expert with extensive experience in the fields of PLC and formal verifications. 
            You are skilled in using analytical methods such as backward questioning and thinking trees to deeply understand ST code and identify any potential vulnerabilities or defects.
             For each potential vulnerability or defect, you analyze the root cause of the issue (which must be based on the Knowledge base).
             I will give you the verification results of the ST code, and you need to analyze the results(both syntax errors and semantic errors) and provide suggestions for improving the code.
             After that, you need to REPAIR ST code based on the requirements and the suggestions you provided
             Here are the relevant files:
             -original requirement: """ + original_requirement + """
             -Refined requirement: """ + usecase_prompt + """
             -ST grammar notes: """ + grammar_prompt + """
             -PLC code: """ + code_prompt + """
             Remember to enclose the PLC ST code within <st_code> and </st_code> tags to clearly mark it in your response(whenever you mention about ST code).
""")

def PLC_Expert(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in PLC coding and requirement analysis."}]
    conversation_history.append({"role": "user", "content": initial_query})
    latest_st_code = None  # 用于存储最新的 ST 代码

    print("Type 'save' to save the latest modified ST code , or 'exit' to quit.")

    while True:
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")

        # 提取响应中的 ST 代码
        match = re.search(r'<st_code>(.*?)</st_code>', str(response), re.DOTALL)
        if match:
            latest_st_code = match.group(1).strip()  # 更新最新代码

        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "save":
            if latest_st_code:
                # 保存 ST 代码到 Modify_Code.txt 和 Modify_Code.scl
                with open("Final_Code.txt", 'w', encoding='utf-8') as f:
                    f.write(latest_st_code)
                with open("Final_Code.scl", 'w', encoding='utf-8') as f:
                    f.write(latest_st_code)
                print("Final ST code saved to Final_Code.txt and Final_Code.scl.")
            else:
                print("No ST code available to save.")
        else:
            conversation_history.append({"role": "user", "content": user_input})
# 启动互动式对话代理
PLC_Expert(query_engine, query_str)