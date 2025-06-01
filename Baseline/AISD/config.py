### !!! warning !!! ###
# Refer to this format of config and write your own api-key in config.py. This canbe imported by your multi agent frameworks.

### must be configged area ###
# model config: refer to src/langchain_create_agent to define it
OPENAI_API_KEY = "sk-xxx"

# config for general url & key are remained (to avoid potential errors)
# you can use model to decide tool-specified url & key:
# (deepseek_base_url, deepseek_api_key & openai_base_url, openai_api_key)
# which correspond to used models in our framework
openai_base_url = "https://api.openai.com/v1"




