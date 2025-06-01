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
# 设置标准输出为 utf-8 编码
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')
warnings.filterwarnings('ignore')
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

folder_path = 'D:\\project\\R2-PLCGen\\ST_Grammar'
# 使用glob模式匹配文件夹中的所有md文件
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
# 使用SimpleDirectoryReader读取所有文件
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))

# 设置全局配置
Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512  # 根据需要设置
Settings.chunk_overlap = 20  # 根据需要设置
def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="oscat_index",
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

initial_requirement = get_prompt_from_file("requirment.txt")
code_prompt = get_prompt_from_file("Modify_Code.txt")
PLC_Task = get_prompt_from_file("PLC_Task_Plan.txt")
# 改进后的提示词设计
query_str = ("""
            You are an expert with extensive experience in the fields of PLC and formal verifications. 
            You are skilled in using analytical methods such as backward questioning and thinking trees to deeply understand ST code and identify any potential vulnerabilities or defects.
             For each potential vulnerability or defect, you analyze the root cause of the issue (which must be based on the Knowledge base).
             I will give you the verification results of the ST code, and you need to analyze the results(both syntax errors and semantic errors) and provide suggestions for improving the code.
             After that, you need to REPAIR ST code based on the requirements and the suggestions you provided.
             I will continue give you the verification results of the REPAIRED ST code, and you need to repair the code in-the-loop.
            """ + "Initial requirement: " + initial_requirement + "PLC coding task::" + PLC_Task +
              "PLC code:" + code_prompt)

def PLC_Expert(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert with extensive experience in the fields of PLC and formal verifications."}]
    conversation_history.append({"role": "user", "content": initial_query})

    while True:
        # 使用完整的对话历史进行查询
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")
        # 保存任务规划
        with open("Final_code.txt", 'w', encoding='utf-8') as f:
            f.write(f"Agent: {response}\n")
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        conversation_history.append({"role": "user", "content": user_input})

# 启动互动式对话代理
PLC_Expert(query_engine, query_str)