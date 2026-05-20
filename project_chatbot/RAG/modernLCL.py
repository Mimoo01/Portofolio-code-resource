from langchain_community.llms import LlamaCpp
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

import ragproses


# =========================
# 1. HYBRID RETRIEVER
# =========================
class HybridRetriever:
    def get_relevant_documents(self, query: str):
        results = ragproses.hybrid_search(query)

        return [
            Document(
                page_content=f"Pertanyaan: {r['pertanyaan']}\nJawaban: {r['jawaban']}",
                metadata={
                    "id": r["id"],
                    "score": r["relevance_score"]
                }
            )
            for r in results
        ]


retriever = HybridRetriever()


# =========================
# 2. LOAD LLM (LlamaCpp)
# =========================
llm = LlamaCpp(
    model_path=r"C:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=350,
    # n_ctx=4096,
    # n_gpu_layers=40,
    verbose=False
)


# =========================
# 3. PROMPT (MODERN LCEL)
# =========================
prompt = ChatPromptTemplate.from_messages([
    ("system",
     "Kamu adalah asisten produk yang membantu menjawab pertanyaan berdasarkan konteks."),
    
    MessagesPlaceholder(variable_name="chat_history"),
    
    ("human",
     "Context:\n{context}\n\nQuestion:\n{input}")
])


# =========================
# 4. RETRIEVAL FUNCTION
# =========================
def format_docs(docs):
    return "\n\n".join([doc.page_content for doc in docs])


def retrieve(query):
    docs = retriever.get_relevant_documents(query)
    return format_docs(docs)


# =========================
# 5. LCEL PIPELINE
# =========================

chain = (
    {
        "context": RunnableLambda(retrieve),
        "input": RunnablePassthrough(),
        "chat_history": RunnablePassthrough()
    }
    | prompt
    | llm
)


# =========================
# 6. SIMPLE CHAT MEMORY
# =========================
chat_history = []  # [(human, ai), ...]


def chat(user_question: str):
    global chat_history

    # convert stored history into LangChain format
    formatted_history = []

    for user, ai in chat_history:
        formatted_history.append(("human", user))
        formatted_history.append(("ai", ai))

    # run chain
    response = chain.invoke({
        "input": user_question,
        "chat_history": formatted_history
    })

    # save memory (IMPORTANT FIX)
    chat_history.append((user_question, response))

    return response

response = chat("produk yg cocok untuk kulit berjerawat")
print(response)