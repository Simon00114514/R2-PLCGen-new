# -*- coding: utf-8 -*-
import warnings
import os
import chardet
import glob
import io
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader,  StorageContext
from llama_index.core import Document
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.postprocessor import SentenceTransformerRerank
from llama_index.llms.openai import OpenAI
from llama_index.core import load_index_from_storage
from llama_index.core import Settings
import sys

sys.stdout  = io.TextIOWrapper(sys.stdout.buffer,  encoding='utf-8', errors='replace')

warnings.filterwarnings('ignore')
# 导入openai模型设置
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")

folder_path = '.D:\\project\\R2-PLCGen\\Property_Info'
# 使用glob模式匹配文件夹中的所有PDF文件
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
# 使用SimpleDirectoryReader读取所有PDF文件,加载文档
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))
# 设置全局配置
Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512  # 根据需要设置
Settings.chunk_overlap = 20  # 根据需要设置

def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        content = file.read()
        # Convert to UTF-8 if necessary
        if encoding != 'GBK':
            content = content.encode('GBK', errors='ignore').decode('GBK')
        return content


def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="property_index",
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
    save_dir="property_index",
)
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)


# get relevant files for the query
spec_format = get_prompt_from_file('property_output_formal.txt')
pattern_explain = get_prompt_from_file("pattern_id_explain.txt")
refined_requirement = get_prompt_from_file("R2IL_design_req.txt")
patterns_file = get_prompt_from_file("Patterns_design.txt")

ctl_str1 = (("""
                You are an expert in Software engineering and you are familiar with the NuSMV model checker and CTL/LTL logic. Your task is to translate the patterns design into CTL or LTL logic specifications. Please follow these guidelines:
                Objective:
                Translate all patterns design into CTL or LTL logic specifications, ensuring compliance with variable design rules, syntax standards, and mutual exclusivity.
                Finally，do not forget to check the missing use cases which are not included in the patterns design. If that happens, translate them into CTL or LTL logic specifications directly.
                Steps:
                1.Variable Design:
                  (1)Comply with specifications.
                  (2)Split event flows with multiple events into separate variables.
                  (3)Ensure mutual exclusivity (e.g., "turn on light" and "turn off light" as separate variables).
                2.Property Specifications:
                  (1)Design CTL/LTL properties (e.g., {1}, {2}) based on the patterns file and CTL/LTL knowledge base.
                  (2)Ensure no patterns or properties are omitted.
                3.Syntax Rules:
                  (1)Use CTL or LTL syntax exclusively; do not mix them.
                  (2)Apply appropriate constraints (e.g., AG, AX, AF, EX, EF) as needed.
                  (3)Never forget to remove {PLC_END}, {PLC_START}, or {EoC} from the specifications.
                4.Output Format:
                  (1)Each pattern must correspond to one CTL or LTL paradigm.
                  (2)Separate specifications with semicolons (;).
                  (3)Include actual descriptions of properties (e.g., "{1}: AG(system_on -> AF heater_on)").
                  (4)Ensure compliance with NuSMV or nuXmv syntax for verification.
                Key Rules:
                  (1)Completeness: Translate all patterns without omission.
                  (2)Precision: Use exact CTL/LTL syntax; avoid mixing or interchanging.
                  (3)Mutual Exclusivity: Define variables to reflect mutually exclusive events.
                  (4)No Refinement: Translate patterns verbatim; do not add extra information or methods.
                Example Output:
                  Pattern Type: pattern-implication [Pattern Name]
                  Formal requirement: AG(({PLC_END} AND (Temperature_Above_Threshold)) -> (Decrease_Inlet_Valve_Opening)) (type: ctl)
                  Final CTL/LTL Specification:
                  {1}: AG(Temperature_Above_Threshold ->  Decrease_Inlet_Valve_Opening);
                  {2}: G(Temperature_Above_Threshold ->  Decrease_Inlet_Valve_Opening);
                """)
            + "patterns definition is:" + pattern_explain + "patterns file：" + patterns_file + "format file：" + spec_format + "refined requirements:" + refined_requirement)

ctl_str2 = (("""
                Please note that the following are separate requirements. You should generate the temporal logic(CTL or LTL) expressions by following the steps bellow: "
                "1.observe the refined requirements,including all the use cases with its' Preconditions/Postconditions, and identify the events and states involved in the system."
                "2.check and analyze the refined requirements,including all the basic flows and alternative flows, and identify the conditions and constraints that need to be considered."
                "3.The CTL or LTL must be based on the refined requirements and nuXmv or NuSMV standards"
                "Here are the relevant files: "
                "please refer to the template or requirements to generate the related files and save them.\n
            """) + "refined requirements:" + refined_requirement)

# 用户选择机制
print("select a desgin for model checking:")
print("1. Patterns+CTL")
print("2. Only CTL")
choice = input("input option(1 or 2):")

# 根据用户选择动态调整内容
if choice == "1":
    selected_choice = ctl_str1
    print("selected Patterns+CTL")
elif choice == "2":
    selected_choice = ctl_str2
    print("selected Only CTL")


def CTLANDLTL_agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in model checking and formal methods."}]
    conversation_history.append({"role": "user", "content": initial_query})

    while True:
        # 使用完整的对话历史进行查询
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)


        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")

        # 保存用例设计
        with open("CTLORLTL_design.txt", 'w', encoding='gbk',errors="replace") as f:
            f.write(f"Agent: {response}\n")

        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        conversation_history.append({"role": "user", "content": user_input})


# 启动互动式对话代理
CTLANDLTL_agent(query_engine, selected_choice)