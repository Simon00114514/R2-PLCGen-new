# -*- coding: utf-8-*-
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
warnings.filterwarnings('ignore')
import sys
import io
# 设置标准输出为 utf-8 编码
sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

folder_path = 'D:\\project\\R2-PLCGen\\ST_Grammar'
# 使用glob模式匹配文件夹中的所有md文件
pdf_files = glob.glob(os.path.join(folder_path, '*.md'))
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

initial_requirement = get_prompt_from_file("requirment.txt")
example_output = get_prompt_from_file("example_plan.txt")
# 改进后的提示词设计
query_str = ("""
                You are a helpful assistant to analyze a PLC (Programmable Logic Controller) task and generate a detailed coding plan. Your task is to:
                    1.Receive a task related to PLC programming (e.g., designing a function block, implementing logic, etc.).
                    2.Retrieve relevant information from your knowledge base or coding library to guide the implementation.
                    3.Generate a concrete coding plan with clear steps to solve the problem.
                Follow these steps:
                    1.Analyze the task:
                    (1) Identify the key requirements (e.g., inputs, outputs, logic, etc.).
                    (2) Break down the task into actionable steps.
                    2.Retrieve relevant information:
                    (1) Search your knowledge base or coding library for relevant examples, concepts, or best practices.
                    (2) Use this information to guide the coding plan.
                    3.Generate the coding plan:
                    (1) List the steps in a structured format, incorporating insights from the retrieved information.
                    (2) Ensure the steps are specific, actionable, and cover all aspects of the task.
                    4.Output the coding plan in the following format:
                    Task: (summary of the task)  
                    Retrieved Information: (relevant information from the knowledge base or coding library)  
                    Coding Plan:  
                                Task 1: (detail of this task)
                                Task 2: (detail of this task)
                                    ...... (continue)
                                Task n: (detail of this task)
                    Key Rules:
                    (1) Accuracy: Ensure the coding plan accurately reflects the task requirements.
                    (2) Completeness: Cover all relevant steps without omission.
                    (3) Clarity: Use clear and concise language for each step.
                    (4) Integration: Incorporate relevant information from the knowledge base or coding library into the plan.
                    Remember only return the complete coding plan, do not output anything else.
            """ + "Initial requirement: " + initial_requirement + "Example output:" + example_output)

def PLC_Task_Planner_agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in PLC coding and requirement analysis."}]
    conversation_history.append({"role": "user", "content": initial_query})

    while True:
        # 使用完整的对话历史进行查询
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")
        # 保存任务规划
        with open("PLC_Task_Plan.txt", 'w', encoding='utf-8') as f:
            f.write(f"Agent: {response}\n")
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        conversation_history.append({"role": "user", "content": user_input})

# 启动互动式对话代理
PLC_Task_Planner_agent(query_engine, query_str)