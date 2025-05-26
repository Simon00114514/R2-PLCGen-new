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

folder_path = 'D:\\project\\R2-PLCGen\\UseCase_Info'
# 使用glob模式匹配文件夹中的所有PDF文件
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
# 使用SimpleDirectoryReader读取所有PDF文件,加载文档
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
        save_dir="usecase_index",
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
    save_dir="usecase_index",
)
query_engine = get_sentence_window_query_engine(index, similarity_top_k=6)



#读取文件
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()


raw_req = get_prompt_from_file("requirment.txt")
usecase_example = get_prompt_from_file("use_case_example.txt")
usecase_i = get_prompt_from_file("R2IL_design_req.txt")
suggestion_req = get_prompt_from_file("R2IL_refined_suggestion.txt")
def select_task():
    print("Choose the refine task you want to perform:")
    print("1. first time refine")
    print("2. refine in the loop")
    task = input("Input 1 or 2:")
    return task
Refine_task = select_task()

initial_refinement_instructions =f"""
You are an expert in requirement engineering and model building.
Your task is to refine the 'Initial Requirement' into a text-based use case diagram.

**Initial Requirement:**
{raw_req}
**Use Case Example (Follow this format):**
{usecase_example}
**Instructions:**
1.  **Output:** Text-based use case diagram ONLY. No code. Adhere strictly to the 'Use Case Example' format.
2.  **Analysis:** Convert all functional aspects of the 'Initial Requirement' into use cases, detailing basic/alternative flows, pre/post-conditions. Consider all system interactions.
3.  **Augmentation (If Needed):** If the 'Initial Requirement' is deficient, propose reasonable additions/clarifications for a complete design, stating assumptions.
4.  **Flows & Errors:** Clearly label flows. Identify and explain any errors in the 'Initial Requirement'.
5.  **Prioritization:** Assign and reflect priority levels for each use case and, if applicable, for flows within use cases.
6.  **Property Reflection:** Ensure all key properties from the 'Initial Requirement' are in the use case design.
Please enclose the the  use case design within <use_case_design> and </use_case_design> tags, and the specifications design within <spec_design> and </spec_design> tags to clearly mark them in your response.
"""

iterative_refinement_instructions = f"""
You are an expert in requirement engineering and model building.
Your task is to refine the 'Current Use Case Design' based on the 'Suggestions for Refinement'.

**Current Use Case Design (to be refined):**
{usecase_i}
**Suggestions:**
{suggestion_req}
**Instructions:**
1.  **Modification:** Incorporate all 'Suggestions for Refinement' into the 'Current Use Case Design'.
2.  **Clarification:** Address ambiguities and supplement information as per the suggestions, using the knowledge base if needed.
3.  **Format:** Maintain the established text-based use case diagram format.
4.  **Output:** Provide the fully updated use case diagram.
Please enclose the the re-designed use case design within <use_case_design> and </use_case_design> tags, and the specifications design within <spec_design> and </spec_design> tags to clearly mark them in your response.
"""
# select one refine task
if Refine_task == "1":
    query_str = (initial_refinement_instructions)

elif Refine_task == "2":
    query_str = (iterative_refinement_instructions)

else:
    print("Invalid input, please input 1 or 2.")
    sys.exit(1)
# 创建互动式对话代理
def Requirement_agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in requirement engineering and model building."}]
    conversation_history.append({"role": "user", "content": initial_query})
    latest_use_case_design = None
    latest_spec_design = None

    print("Type 'save' to save the latest use case and specification designs, or 'exit' to quit.")
    while True:
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")

        # 提取响应中的 use case design 和 spec design
        use_case_match = re.search(r'<use_case_design>(.*?)</use_case_design>', str(response), re.DOTALL)
        spec_match = re.search(r'<spec_design>(.*?)</spec_design>', str(response), re.DOTALL)
        if use_case_match:
            latest_use_case_design = use_case_match.group(1).strip()
        if spec_match:
            latest_spec_design = spec_match.group(1).strip()

        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "save":
            if latest_use_case_design and latest_spec_design:
                # 保存到 R2IL_refined_suggestion.txt
                with open("R2IL_design_req.txt", 'w', encoding='utf-8') as f:
                    f.write(
                        "### Use Case Design\n\n" + latest_use_case_design + "\n\n### Specifications Design\n\n" + latest_spec_design)
            else:
                print("No designs available to save.")
        else:
            conversation_history.append({"role": "user", "content": user_input})


# 启动互动式对话代理
Requirement_agent(query_engine, query_str)