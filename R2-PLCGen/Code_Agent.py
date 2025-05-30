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
# change the path to your own
folder_path = 'D:\\project\\R2-PLCGen\\ST_Grammar'
md_files = glob.glob(os.path.join(folder_path, '*.md'))
documents = SimpleDirectoryReader(input_files=md_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))

Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512
Settings.chunk_overlap = 20
def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="ST_Grammar_index",
):
    # create node parser
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

# define files access
def get_prompt_from_file(file_path):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, 'r', encoding=encoding) as file:
        return file.read()

usecase_prompt = get_prompt_from_file("R2IL_refined_suggestion.txt")
grammar_prompt = get_prompt_from_file("st_rules.txt")
original_prompt = get_prompt_from_file("requirment.txt")
# main prompt
query_str = ("""
    You are a talented PLC ST coder. Help me generate PLC ST code based on the following requirements.
    Please note that the following are separate requirements. You should generate the ST code by following these steps:
    1. Observe the original requirements.
    2. Check and analyze the refined requirements, then generate ST code.
    3. The PLC ST code must be based on the refined requirements and comply with IEC 61131-3 standards.
    4. Strictly adhere to the syntax rules in the vector store (preferably Siemens SCL syntax).
    Here are the relevant files:
    - Original requirements: """ + original_prompt + """
    - Details of Refined requirement: """ + usecase_prompt + """
    - ST grammar notes: """ + grammar_prompt + """
    Please enclose the PLC ST code within <st_code> and </st_code> tags to clearly mark it in your response.
""")

def PLC_Coder(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in PLC coding and requirement analysis."}]
    conversation_history.append({"role": "user", "content": initial_query})
    latest_st_code = None  # save the latest ST code

    print("Type 'save' to save the latest ST code to Modify_Code.txt and Modify_Code.scl, or 'exit' to quit.")

    while True:
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")
        print("Type 'save' to save the latest use case and specification designs to R2IL_refined_suggestion.txt, or 'exit' to quit.")
        # extract the ST code from the response
        match = re.search(r'<st_code>(.*?)</st_code>', str(response), re.DOTALL)
        if match:
            latest_st_code = match.group(1).strip()  # 更新最新代码

        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "save":
            if latest_st_code:
                # 保存 ST 代码到 Modify_Code.txt 和 Modify_Code.scl
                with open("Modify_Code.txt", 'w', encoding='utf-8') as f:
                    f.write(latest_st_code)
                with open("Modify_Code.scl", 'w', encoding='utf-8') as f:
                    f.write(latest_st_code)
                print("ST code saved to Modify_Code.txt and Modify_Code.scl")
            else:
                print("No ST code available to save.")
        else:
            conversation_history.append({"role": "user", "content": user_input})

# interaction with the agent
PLC_Coder(query_engine, query_str)