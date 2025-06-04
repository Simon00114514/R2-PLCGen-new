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
folder_path = 'SMV_Info'
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))
Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512
Settings.chunk_overlap = 20

def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="smv_index",
):
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
    save_dir="smv_index",
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
use_case_grammar = get_prompt_from_file("use_case_grammar.txt")
spec_prompt = get_prompt_from_file("CTLORLTL_design.txt")
use_case_design = get_prompt_from_file("R2IL_design_req.txt")


# prompt for guiding req_Agent
query_str = ("""
    You are an expert-level programmer in the field of computer formal verification and modeling, with years of programming experience and rich expertise in model design and verification techniques.
    You are proficient in various CTL/LTL and SMV tools and are capable of designing CTL formulas or SMV models based on actual requirements.
    The following are the original and refined requirements documents, the patterns constraints file generated based on them, and the CTL/LTL files generated from the patterns file respectively.
    First, check whether the generated use case diagram contains syntax rule violations based on the syntax rules of use case diagrams;
    Next, perform a preliminary check for obvious descriptive differences or hidden conditions not explicitly stated between the original and refined requirements. After verifying compliance with syntax rules, assign a score (out of 10, where 10 indicates all RUs are satisfied);
    Next, based on the semantic inconsistencies between the original and refined requirements (I will provide the formal verification results identifying semantic conflicts), assist in modifying the refined requirements.
    Note: Do not provide programming code. Focus solely on modeling and modification tasks. Below are relevant files; please generate and save associated files by referencing templates or requirements.
    YOU should only return to me the score of the refined requirements and your comments based on your revision.
    Finally, you should wait for the feedback of the semantic verification results, and give the modification suggestions for re-design this refined requirements based on the feedback.
    Also, the re-designed refined requirement should always keep the same format as the prior one.
    Please enclose the the re-designed use case design within <use_case_design> and </use_case_design> tags, and the specifications design within <spec_design> and </spec_design> tags to clearly mark them in your response.
    """ + "Initial requirement: " + initial_requirement + "Refined requirement:" + use_case_design + "use case grammar notes:" + use_case_grammar + "Specifications design:" + spec_prompt)
def Req_Agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert-level programmer in the field of computer formal verification and modeling, with years of programming experience and rich expertise in model design and verification techniques."}]
    conversation_history.append({"role": "user", "content": initial_query})
    latest_use_case_design = None
    latest_spec_design = None

    print("Type 'save' to save the latest use case and specification designs to R2IL_refined_suggestion.txt, or 'exit' to quit.")

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
                with open("R2IL_refined_suggestion.txt", 'w', encoding='utf-8') as f:
                    f.write("### Use Case Design\n\n" + latest_use_case_design + "\n\n### Specifications Design\n\n" + latest_spec_design)
            else:
                print("No designs available to save.")
        else:
            conversation_history.append({"role": "user", "content": user_input})

# interaction with the agent
Req_Agent(query_engine, query_str)