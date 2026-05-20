from langchain_classic.chains import create_history_aware_retriever
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_retrieval_chain
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_classic.chains.combine_documents import (
    create_stuff_documents_chain,
)
from langchain_community.llms import LlamaCpp


contextualize_q_system_prompt = """
Diberikan riwayat percakapan dan pertanyaan terbaru dari pengguna
yang mungkin merujuk pada konteks dalam riwayat percakapan,
buatlah pertanyaan mandiri (standalone question)
yang dapat dipahami tanpa melihat riwayat percakapan.
Jangan menjawab pertanyaannya,
cukup ubah formulasinya jika diperlukan,
atau kembalikan seperti aslinya jika sudah jelas.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


qa_system_prompt = """
Kamu adalah asisten untuk tugas tanya jawab.
jawablah dengan menggunakan bahasa yang ramah dan kalimat yang lengkap.
Gunakan potongan konteks yang berhasil diambil berikut untuk menjawab pertanyaan.
Jika kamu tidak mengetahui jawabannya, cukup katakan bahwa kamu tidak tahu.
Gunakan maksimal tiga kalimat dan buat jawaban tetap singkat serta jelas.
{context}
"""

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

llm = LlamaCpp(
    model_path=r"C:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0.Q4_K_M.gguf",
    temperature=0.7,
    max_tokens=350,
    verbose=False
)

# retriever = BM25Retriever.from_texts(["Saat ini kami memiliki beberapa tipe produk seperti serum, toner, cleanser, dan Moisturizer"],["saat ini kami memiliki beberapa produk yang cocok untuk kulit berjerawat tergantung dari anda memilih produk yang mana antara lain serum daily purify,toner skin booster untuk kulit berjerawat,dan fasial wash purify untuk segala jenis kulit "])

retriever = BM25Retriever.from_documents(
    [
        Document(page_content="Saat ini kami memiliki beberapa tipe produk seperti serum, toner, cleanser, dan Moisturizer"),
        Document(page_content="saat ini kami memiliki beberapa produk yang cocok untuk kulit berjerawat tergantung dari anda memilih produk yang mana antara lain serum daily purify,toner skin booster untuk kulit berjerawat,dan fasial wash purify untuk segala jenis kulit"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)


question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)


from langchain_core.messages import HumanMessage

chat_history = []

question = "sebutkan  produk  produk  apa saja yang dijual"

ai_msg_1 = rag_chain.invoke({"input": question, "chat_history": chat_history})
chat_history.extend([HumanMessage(content=question), ai_msg_1["answer"]])
print("test masuk")
print(ai_msg_1["answer"])

second_question = "kalau untuk kulit berjerawat apakah ada"
ai_msg_2 = rag_chain.invoke({"input": second_question, "chat_history": chat_history})
print(ai_msg_2["answer"])

second_question = "coba  rangkumkan  pertanyaan saya apa aja tadi"
ai_msg_3= rag_chain.invoke({"input": second_question, "chat_history": chat_history})
print(ai_msg_3["answer"])









