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
import codecs
import io
# 设置标准输出为 UTF-8 编码
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='gbk', errors='replace')

# 忽略警告信息
warnings.filterwarnings('ignore')

# 导入openai模型设置
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

# 设置全局配置
Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512  # 根据需要设置
Settings.chunk_overlap = 20  # 根据需要设置

# 定义数据文件夹路径
folder_path = 'D:\\project\\R2-PLCGen\\Property_Info'

# 使用 glob 模式匹配文件夹中的所有 PDF 文件
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))

# 使用 SimpleDirectoryReader 读取所有 PDF 文件，加载文档
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))


def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="plcverif_index",
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
    # 定义后处理器
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )

    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=similarity_top_k, node_postprocessors=[postproc, rerank]
    )
    return sentence_window_engine


# 构建索引
index = build_sentence_window_index(
    [document],
    save_dir="plcverif_index",
)

# 获取查询引擎
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)


# 定义函数从文件中获取提示词
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()


# input files:
usecase_file = get_prompt_from_file("R2IL_design_req.txt")
patterns_explain = get_prompt_from_file("pattern_id_explain.txt")
patterns_example = get_prompt_from_file("patterns_design_example.txt")



# prompt design:
pattern_translation_instructions = f"""
You are an expert in software engineering and formal methods, specializing in requirement pattern mapping and CTL/LTL specification generation.
Your task is to translate the provided 'Refined Use Case Design' into predefined requirement patterns and generate corresponding CTL/LTL formulas.

**Refined Use Case Design (Input):**
{usecase_file}
**Reference - Requirement Patterns Explanation (Consult this for pattern understanding):**
{patterns_explain}
**Reference - Output Format Example (Strictly follow this JSON structure):**
{patterns_example}
"""

# 改进后的提示词设计
query_str = (pattern_translation_instructions)


# 创建互动式对话代理
def Pattern_agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in requirement engineering and model building."}]
    conversation_history.append({"role": "user", "content": initial_query})

    while True:
        # 使用完整的对话历史进行查询
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")
        # 保存用例设计
        with open("Patterns_design.txt", 'w', encoding='GBK',errors="replace") as f:
            f.write(f"Agent: {response}\n")
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        conversation_history.append({"role": "user", "content": user_input})


# 启动互动式对话代理
Pattern_agent(query_engine, query_str)