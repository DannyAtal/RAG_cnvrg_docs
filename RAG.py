import torch
from transformers import BitsAndBytesConfig
from llama_index.prompts import PromptTemplate
from llama_index.llms import HuggingFaceLLM
from llama_index import SimpleDirectoryReader
from llama_index import ServiceContext
from llama_index import VectorStoreIndex
from llama_index.response.notebook_utils import display_response
import gradio as gr

# Load documents and instantiate the model outside the function
documents = SimpleDirectoryReader('/cnvrg/Data/').load_data()

quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
)

llm = HuggingFaceLLM(
    model_name="codellama/CodeLlama-7b-Instruct-hf",
    tokenizer_name="codellama/CodeLlama-7b-Instruct-hf",
    query_wrapper_prompt=PromptTemplate("<s> [INST] {query_str} [/INST] "),
    context_window=3900,
    model_kwargs={"quantization_config": quantization_config},
)

service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-small-en-v1.5")
vector_index = VectorStoreIndex.from_documents(documents, service_context=service_context)
query_engine = vector_index.as_query_engine(response_mode="compact")

def get_model_response(message, history):
    # Use the pre-loaded model for queries
    response = query_engine.query(message)

    # Check if the response is a string or can be converted to a string
    if isinstance(response, str):
        first_line_response = response.split('\n')[0]
    else:
        # If the response is not a string, attempt to convert it to a string
        try:
            response_str = str(response)
            first_line_response = response_str.split('\n')[0]
        except Exception as e:
            # If unable to convert to string, handle the error accordingly
            first_line_response = "Error processing response: " + str(e)

    return first_line_response


iface = gr.ChatInterface(
    fn=get_model_response,
    #inputs=gr.Textbox(),
    #outputs=gr.Textbox(),
    title="CNVRG CLI2 Chatbot",
    description="Enter your coding-related query to get responses!",
)

iface.launch(share=True)
