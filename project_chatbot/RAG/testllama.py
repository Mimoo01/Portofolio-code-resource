from llama_cpp import Llama
from sentence_transformers import SentenceTransformer
import psycopg2
import ragproses

# llm = Llama(
#     model_path=r"C:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0.Q4_K_M.gguf",
#     n_gpu_layers=40  # important: enables GPU offload
# )


def embeeding_text(input):
    model = SentenceTransformer('firqaaa/indo-sentence-bert-base')
    embeddings = model.encode(input)
    print("embedding text",embeddings)

def get_connection():
    """Membuat koneksi ke database PostgreSQL dan mengembalikan objek koneksi."""
    
    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )
    return conn


llm = Llama (
    model_path=r"C:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0.Q4_K_M.gguf",
    n_threads=10,  # jika ingin lebih cepat, sesuaikan dengan jumlah core CPU,
    n_ctx=3000,
    # n_gpu_layers=30,
    n_batch=521,
    verbose=True
)

input = "Produk apa saja yang cocok untuk kulit berjerawat?"

context = ragproses.hybrid_search(input)

full_context = (
    "Kamu merupakan virtual asistant yang membantu customer dalam menjawab seputar informasi yang berada pada jeanue Beauty kamu dapat menjawab setiap pertanyaan dari user dengan mengikuti aturan berikut : \n"
    "1. jawablah dengan menggunakan bahasa yang ramah tetapi tetap menggunakan inti informasi dari konteks'.\n"
    "Berikut merupakan konteks yang diberikan :\n"
    f"{context}\n"
)

response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": full_context},
            {"role": "user", "content": input}
        ],
        max_tokens=3072,
)

print(response)
embeeding_text(input)




