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
import re
sys.stdout = codecs.getwriter("gbk")(sys.stdout.detach())

warnings.filterwarnings('ignore')
try:
    from config import chat_model, openai_api_key, openai_base_url
except ImportError:
    print("[WARN] config.py not found or variables missing. Using defaults/environment variables.")
# change the path to your own
folder_path = 'D:\\project\\R2-PLCGen\\SMV_Info'
# access all pdf files in the folder
pdf_files = glob.glob(os.path.join(folder_path, '*.pdf'))
# use SimpleDirectoryReader to read all PDF files
documents = SimpleDirectoryReader(input_files=pdf_files).load_data()
document = Document(text="\n\n".join([doc.text for doc in documents]))
# LLM sets
Settings.llm = OpenAI(model="o3-mini", temperature=0.1)
Settings.chunk_size = 512  # setting chunk size
Settings.chunk_overlap = 20  # setting chunk overlap

def build_sentence_window_index(
        documents,
        embed_model="local:BAAI/bge-large-en-v1.5",
        sentence_window_size=3,
        save_dir="smv_index",
):
    # create sentence window node parser
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


# 加载文件内容

requirment_file = get_prompt_from_file("requirment.txt")
smv_example = get_prompt_from_file('SMV_example.txt')
spec_prompt1 = get_prompt_from_file('CTLORLTL_design.txt')
spec_prompt2 = get_prompt_from_file('CTLORLTL_initial_design.txt')
smv_example2 = get_prompt_from_file('SMV_grammar_example.txt')


# select different task
def select_task():
    print("Choose the task you want to perform:")
    print("1. check the semantic consistency of the specification")
    print("2. check the syntax of the specification ")
    task = input("Input 1 or 2:")
    return task

#  task 1 or task 2
task = select_task()
if task == "1":
    query_str = ("""
    To design an SMV model for verifying semantic consistency, please consider the following guidelines:
        1.Exclusion of assign Definitions:  
            The SMV model should not contain any assign sections.
        2.Variable Selection:
            Include only variables derived from the CTL or LTL expressions corresponding to both the refined and original requirements.
        3.Identifying Corresponding Expressions:
            Select pairs of CTL/LTL expressions from both refined and original requirements that are semantically similar. For example, if the refined requirement states: "1. For the basic flow where the conveyor belt starts moving when an object is detected and the stop button is not pressed:" and the original requirement states: "The sensor detects an object and the conveyor belt starts if the user does not press stop," these two expressions are considered semantically similar and should be selected for constructing the implication.
        4.Constructing Implication Expressions:
            Formulate implications where the CTL/LTL expression from the refined requirement implies the corresponding expression from the original requirement. The structure should be: CTL(Refined Requirement) -> CTL(Original Requirement). Ensure that the left side of the implication comes from the refined requirements, and the right side from the original requirements.
        5.Scope of Consideration:
            Focus on functional requirements. If a CTL/LTL expression in the refined requirements pertains to non-functional aspects and has no counterpart in the original requirements, it can be excluded from the implication construction.
        6.Balanced Comparison:
            Avoid constructing implications using expressions from only one set of requirements. Ensure that each implication relates a refined requirement to its original counterpart.
        7.Order of Implication:
            Maintain the correct order in implications: the refined requirement's expression should imply the original requirement's expression (Refined -> Original). Do not reverse this order.
        8.Combining Multiple Expressions:
            If multiple expressions from the refined requirements collectively correspond to a single expression in the original requirements, combine these refined expressions using the '&' (AND) operator before forming the implication.
        9.Preservation of Original Expressions:
            Do not modify the CTL/LTL expressions derived from the original requirements. They should remain as initially defined.
        10.Comprehensive Inclusion:
            Include all relevant CTL/LTL expressions from the refined requirements in the analysis, covering basic flows, alternative flows, and special cases.
        11.One-to-One Correspondence:
            Ensure that each implication corresponds directly to a pair of related expressions. For instance, if there is only one expression in the original requirements, construct implications solely related to that expression without introducing unrelated expressions.
        Please enclose the SMV model code within <smv_model> and </smv_model> tags.
    """
    + "SMV model template:" + smv_example  + "refined requirement specifications:" + spec_prompt1 + "initial requirement specifications:" + spec_prompt2)
elif task == "2":
    query_str = ("""
                    To design an SMV model for verifying syntactic correctness, please consider the following guidelines:
                    1.Exclusion of assign Definitions:
                       The SMV model should not contain any assign sections.
                    2.Variable Selection:
                        Include only variables derived from the CTL or LTL expressions corresponding to the refined requirements.
                    3.Direct Adoption of Refined Requirement Expressions:
                        Use the property expressions from the refined requirements directly in the LTLSPEC or CTLSPEC sections of the SMV model.
                    4.Compliance with NuSMV Syntax Rules:
                        Ensure that the model adheres to NuSMV's syntax rules, eliminating any unused or redundant variables.
                    Please enclose the SMV model code within <smv_model> and </smv_model> tags.
    """ + "SMV model template:" + smv_example2 + "refined requirement specifications:"+ spec_prompt1)
else:
    print("Error Task number!")
    exit()

# 互动式代理
def smv_agent(query_engine, initial_query):
    conversation_history = [{"role": "system", "content": "You are an expert in SMV model construction. You will be given a set of refined requirements and an initial set of requirements."
                                                          " Your task is to construct an SMV model that verifies the syntactic correctness of the refined requirements based on the initial requirements. "
                                                          "You should follow the guidelines provided to ensure the model is accurate and complete."}]
    conversation_history.append({"role": "user", "content": initial_query})
    latest_smv_model = None

    print("Type 'save' to save the latest SMV model to test.smv, or 'exit' to quit.")

    while True:
        full_query = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history])
        response = query_engine.query(full_query)
        conversation_history.append({"role": "assistant", "content": str(response)})
        print(f"Agent: {response}")

        # 提取响应中的 SMV 模型
        match = re.search(r'<smv_model>(.*?)</smv_model>', str(response), re.DOTALL)
        if match:
            latest_smv_model = match.group(1).strip()  # 更新最新模型

        # save the complete response (including "Agent: ") to the log file
        with open("smv_check_design.txt", 'w', encoding='gbk', errors="replace") as f:
            f.write(f"Agent: {response}\n")

        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        elif user_input.lower() == "save":
            if latest_smv_model:
                with open("test.smv", 'w', encoding='gbk', errors="replace") as f:
                    f.write(latest_smv_model)
                print("SMV model saved to test.smv")
            else:
                print("No SMV model available to save.")
        else:
            conversation_history.append({"role": "user", "content": user_input})
# initiate smv agent
smv_agent(query_engine, query_str)