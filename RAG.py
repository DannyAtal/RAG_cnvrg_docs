import gradio as gr
import torch
from llama_index import SimpleDirectoryReader
from transformers import BitsAndBytesConfig
from llama_index.prompts import PromptTemplate
from llama_index.llms import HuggingFaceLLM
from llama_index import ServiceContext
from llama_index import VectorStoreIndex

# Define the conversation_history outside the function for persistence
conversation_history = []

# Load documents and create the model, vector index, and query engine
documents = SimpleDirectoryReader('/cnvrg/dataset_creating/').load_data()
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
    device_map="auto",
)

service_context = ServiceContext.from_defaults(llm=llm, embed_model="local:BAAI/bge-small-en-v1.5")
vector_index = VectorStoreIndex.from_documents(documents, service_context=service_context)
query_engine = vector_index.as_query_engine(response_mode="compact")

def chat_interface(user_input):
    global conversation_history

    # Check for exit condition
    if user_input.lower() == 'exit':
        conversation_history = []  # Reset conversation history
        return "Conversation reset. Enter your question again."

    # Add user input to conversation history
    conversation_history.append(user_input)

    # Query the model with the entire conversation history
    response = query_engine.query(' '.join(conversation_history))

    # Extract the response text
    response_text = response.text if hasattr(response, 'text') and isinstance(response.text, str) else str(response)

    # Add model's response to conversation history
    conversation_history.append(response_text)

    return response_text

# Create a Gradio interface
iface = gr.Interface(
    fn=chat_interface,
    inputs=gr.Textbox(),
    outputs=gr.Textbox(),
    live=True,  # Enables live updates without requiring a button click
    title="Conversational Model",
    description="Enter your questions to interact with the model.",
)

# Launch the Gradio interface on an external URL
iface.launch(share=True)
