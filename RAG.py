import torch
from transformers import BitsAndBytesConfig
from llama_index.prompts import PromptTemplate
from llama_index.llms import HuggingFaceLLM
from llama_index import SimpleDirectoryReader
from llama_index import ServiceContext
from llama_index import VectorStoreIndex
from llama_index.response.notebook_utils import display_response
import gradio as gr

def get_model_response(query):
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

    response = query_engine.query(query)

    return response

iface = gr.Interface(
    fn=get_model_response,
    inputs=gr.Textbox(),
    outputs=gr.Textbox(),
    live=False,
    title="CNVRG CLI2 Chatbot",
    description="Enter your coding-related query to get responses!",
)

iface.launch(share=True)
