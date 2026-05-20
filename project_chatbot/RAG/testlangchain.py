from langchain_community.llms import LlamaCpp
from langchain_core.prompts import PromptTemplate
import ragproses

# Load model
llm = LlamaCpp(
    model_path=r"C:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=350,
    n_ctx=4096,
    n_gpu_layers=40
)

context = ragproses.hybrid_search("Kalau disini produk tonner nya apa aja ya?")



# Prompt template
prompt = PromptTemplate.from_template("""
Kamu adalah AI Assistant yang membantu customer untuk menjawab informasi mengenai produk produk dari peau june
jawablah pertanyaan yang diberikan customer dengan menggunakan context berikut :
Konteks database :
{context}

Pertanyaan user:
{question}

Jawaban:
""")

# Chain modern
chain = prompt | llm

# Invoke
response = chain.invoke({
    "context":context,
    "question": "Kalau disini produk tonner nya apa aja ya",
})

print(response)