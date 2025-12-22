
# EXAMPLE 2 
import time
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer,util
from nltk import word_tokenize
from nltk.corpus import stopwords
import psycopg2
import cohere
from datetime import datetime
import json
from collections import Counter
from flask import Flask, request, jsonify

def get_connection():
    """Membuat koneksi ke database PostgreSQL dan mengembalikan objek koneksi."""
    
    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )
    return conn


# embedding_model = SentenceTransformer('sentence-transformers/LaBSE')
embedding_model = SentenceTransformer("firqaaa/indo-sentence-bert-base")

def split_into_trigrams(text):
    import re
    if isinstance(text, list):
        text = " ".join(text)  # join jika input list
    words = re.findall(r'\w+', text.lower())
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]
    return trigrams

def getsubtopic():
    conn = get_connection()
    query = """
    SELECT DISTINCT LOWER(TRIM(cknowledgesubtopic)) AS cleaned_subtopic FROM mtknowledgebase;
    """
    with conn.cursor() as curr:
        curr.execute(query)
        # rows = curr.fetchall()
        rows = [row[0] for row in curr.fetchall()]
    return rows

def getopic():
    conn = get_connection()
    query = """
    SELECT DISTINCT LOWER(TRIM(cknowledgetopic)) AS cleaned_topic FROM mtknowledgebase;
    """
    with conn.cursor() as curr:
        curr.execute(query)
        # rows = curr.fetchall()
        rows = [row[0] for row in curr.fetchall()]
    return rows

def guide_knowledge(question, answer,topic,subtopic):
    print("Masuk guideknowledge")
    llm = Llama (
    model_path = r"D:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0-Q6_K.gguf",
    n_threads=12, 
    n_ctx=3000,
    # n_gpu_layers=30,
    n_batch=2048,
    verbose=True
    )
    print("tipe answer",type(answer))
    # 1. Pecah jadi trigram
    trigrams = split_into_trigrams(answer)
    print("Total trigrams:", len(trigrams))
    subtopiclist = getsubtopic()
    print("sub topic",subtopic)
    formatted_subtopics = "\n".join(f"{i+1}. {sub}" for i, sub in enumerate(subtopiclist))
    topiclist = getopic() 
    print("topic",topiclist)
    formatted_topic = "\n".join(f"{i+1}. {sub}" for i, sub in enumerate(topiclist))



    # 2. Template jawaban default
    templates = [
        "tidak ada konteks yang relevan, mohon hubungi admin lebih lanjut",
        "maaf, saya tidak bisa menjawab pertanyaan kamu",
        "tidak ada konteks"
        "tidak ada informasi",
        "tidak bisa memberikan ",
        "tidak disebutkan didalam informasi"
    ]

    # 3. Encode template dan trigram
    template_embeddings = embedding_model.encode(templates, convert_to_tensor=True)
    trigram_embeddings = embedding_model.encode(trigrams, convert_to_tensor=True)

    # 4. Hitung similarity
    similarities = util.pytorch_cos_sim(trigram_embeddings, template_embeddings)
    max_per_trigram = similarities.max(dim=1).values

    print("\nSimilarity per trigram:")
    for trigram, score in zip(trigrams, max_per_trigram):
        print(f"{trigram} → similarity: {score.item():.4f}")

    # 5. Cek overall similarity
    overall_similarity = float(max_per_trigram.max())
    print("Overall similarity:", overall_similarity)


    full_context = ()


    # 6. Proses jika tidak terjawab dengan baik
    if overall_similarity > 0.75:
        print("Pertanyaan tidak bisa terjawab dengan sempurna atau customer tidak puas terhadap jawaban")
        if topic == "" or subtopic == "":
            print("topik atau sub topic kosong")
            full_context = (
                "Anda adalah asisten virtual yang bertugas membantu admin untuk:\n"
                "- Memberikan saran tentang data/informasi apa yang sebaiknya ditambahkan ke dalam database agar dapat menjawab pertanyaan berikut dengan lebih baik.\n\n"
                "Berikan klasifikasi apakah pertanyaan masuk ke dalam salah satu subtopik berikut ini. "
                "Jika tidak, maka kategorikan ke dalam 'lain-lain'. Berikut daftar subtopik:\n"
                f"{formatted_subtopics}\n\n"
                "Berikanlah juga klasifikasi apakah pertanyaan termasuk kedalam topic apa berdasarkan 3 kategori topik dibawah ini : "
                f"{formatted_topic}\n"
                "Jawaban Anda harus diberikan dalam format JSON dengan struktur sebagai berikut:\n\n"
                "{\n"
                "  \"saran\": \"Halo Admin, mohon masukkan informasi mengenai...\",\n"
                "  \"topik\": \"\"\n"
                "  \"sub topik\": \"\"\n"
                "}\n\n"
                f"Konteks:\n"
                f"Pertanyaan: {question}\n"
                f"Jawaban: {answer}\n"
            )
        elif topic != "" or subtopic !="":
                print("topic sub topik ada isinya")
                full_context = (
                "Anda adalah asisten virtual yang bertugas membantu admin untuk:\n"
                "- Memberikan saran tentang data/informasi apa yang sebaiknya ditambahkan ke dalam database agar dapat menjawab pertanyaan berikut dengan lebih baik.\n\n"
                "Jawaban Anda harus diberikan dalam format JSON dengan struktur sebagai berikut:\n\n"
                "{\n"
                "  \"saran\": \"Halo Admin, mohon masukkan informasi mengenai...\",\n"
                "}\n\n"
                f"Konteks:\n"
                f"Pertanyaan: {question}\n"
                f"Jawaban: {answer}\n"
            )
    # 7. Jika jawaban sudah cukup
    elif overall_similarity <= 0.75:
        if topic == "" or subtopic == "":
            full_context = (
                "Anda adalah asisten virtual yang bertugas membantu admin untuk:\n"
                "- Memberikan saran tentang data/informasi apa yang sebaiknya ditambahkan ke dalam database agar dapat menjawab pertanyaan berikut dengan lebih baik.\n\n"
                "Berikan klasifikasi apakah pertanyaan masuk ke dalam salah satu subtopik berikut ini. "
                "Jika tidak, maka kategorikan ke dalam 'lain-lain'.jangan menerjemahkan sub topic kedalam bahasa indonesia tetap sesuai yang diberikan berdasarkan daftar sub topik nya. Berikut daftar subtopik:\n"
                f"{formatted_subtopics}\n\n"
                "Berikanlah juga klasifikasi apakah pertanyaan termasuk kedalam topik apa berdasarkan  kategori topik dibawah ini : "
                f"{formatted_topic}\n"
                "Jawaban Anda harus diberikan dalam format JSON dengan struktur sebagai berikut:\n\n"
                "{\n"
                "  \"topik\": \"\"\n"
                "  \"sub topik\": \"\"\n"
                "}\n\n"
                f"Konteks:\n"
                f"Pertanyaan: {question}\n"
                f"Jawaban: {answer}\n"
            )
        elif topic != "" or subtopic != "":
            print("pertanyaan dapat terjawab, topik subtopik ada semua ")
            return "Pertanyaan dapat terjawab dengan baik",topic,subtopic;
 
    print("full contex",full_context)
    guideresponse = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": full_context},
                {"role": "user", "content": question}
            ],
            max_tokens=1024,
        )

    raw_response = guideresponse["choices"][0]["message"]["content"]
    print("LLM Raw Response:", raw_response)
    try:
        response_json = json.loads(raw_response)
        saran = response_json.get("saran", "Tidak ada saran")
        topic = response_json.get("topik",topic)
        subtopic = response_json.get("sub topik",subtopic)
    except json.JSONDecodeError:
        print("⚠️ Gagal parsing JSON, fallback ke string biasa")
        saran = raw_response
    return saran,topic,subtopic

def insertresponsetodb(sessionid,name,topic,subtopic,question,answer,suggestion):
    try:
        conn = get_connection()
        curr = conn.cursor()
        getdate = datetime.now()
        query = """
                INSERT INTO mtlogquestionuser
                (csessionid, cname, ctopic,csubtopic,cquestion,canswer,date,csuggestion) 
                VALUES (%s, %s, %s, %s,%s,%s,%s,%s)
                """
        curr.execute(query, (sessionid,name,topic,subtopic,question,answer,getdate,suggestion))
        conn.commit()
        conn.close()
        print("insert berhasil")

    except Exception as e:
        print("error saat insert ke database:", e)

def get_embedding_st(text):
    start = time.time()
    embeddings = embedding_model.encode(text)
    print("max sequence length",embedding_model.max_seq_length)
    end = time.time()
    print(f"[WAKTU] Embedding selesai dalam {end - start:.2f} detik")
    return embeddings

def similarity_search(question):
    start = time.time()
    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )
    cur = conn.cursor()
    print("mulai embedding dan similarity search...")
    query_embedding = get_embedding_st(question)
    embedding_string = f"[{','.join(map(str, query_embedding))}]"
    # Cosine Similiarity 
    cur.execute("""
        SELECT cid,cknowledgetopic,cknowledgetopicinformation,cknowledgesubtopic,cknowledgeinformation, 1 - (cknowledgembedding <=> %s::vector) AS similarity
        FROM mtknowledgebase
        WHERE 1 - (cknowledgembedding <=> %s::vector) > 0.5
        ORDER BY similarity DESC
        LIMIT 5;
    """, (embedding_string,embedding_string))

    # cur.execute("""
    #     SELECT cid,cknowledgeinformation, 1 - (embedding_information <=> %s::vector) AS similarity , cknowledgetopic
    #     FROM mtknowledgebase
    #     ORDER BY similarity DESC
    #     LIMIT 5;
    # """, (embedding_string,))
 
    rows = cur.fetchall()
    conn.close()
    end = time.time()
    print("hasil similiarity search",rows)
    print(f"[WAKTU] Similarity search selesai dalam {end - start:.2f} detik")
    return rows


def keyword_search(query):
    custom_keyword = ['cocok','bagus','rekomendasi','rekomendasikan','aja','sebutkan','jelaskan','?']

    stop_words = stopwords.words('indonesian')
    all_stopwords = set(stop_words + custom_keyword)

    tokens = word_tokenize(query.lower())
    filtered_tokens = [word for word in tokens if word not in all_stopwords]
    print("filtered tokens", filtered_tokens)

    tsquery_string = ' | '.join(filtered_tokens)

    query = f"""
    WITH ranked AS (
    SELECT *,
            ts_rank(to_tsvector('indonesian', cknowledgeinformation), to_tsquery('indonesian', %s)) AS raw_score
    FROM mtknowledgebase
    WHERE to_tsvector('indonesian', cknowledgeinformation) @@ to_tsquery('indonesian', %s)
    ),
    normalized AS (
    SELECT 
        cknowledgeinformation,
        cknowledgetopic,
        cknowledgesubtopic,
        raw_score,
        CASE 
        WHEN MAX(raw_score) OVER () = MIN(raw_score) OVER () THEN 1.0 -- Jika semua skor sama, normalisasi jadi 1
        ELSE (raw_score - MIN(raw_score) OVER ())::float / (MAX(raw_score) OVER () - MIN(raw_score) OVER ())
        END AS normalized_score
    FROM ranked
    )
    SELECT cknowledgeinformation, cknowledgetopic,cknowledgesubtopic, normalized_score
    FROM normalized
    WHERE normalized_score > 0.7
    ORDER BY normalized_score DESC;

    """

    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )

    cur = conn.cursor()
    cur.execute(query, (tsquery_string, tsquery_string))

    results = cur.fetchall()
    print("keyword search result", results)
    cur.close()
    conn.close()
    
    return results



def hybrid_search(question):
    print("Masuk hybrid search method")

    # Vector search result 
    similarity_result = similarity_search(question)

    # Keyword search result 
    # trigram_result = trigram_search(question)
    keyword_result = keyword_search(question)

    # Gabungkan hasil dari vector search dan keyword search
    # combined_search = [row[1] for row in similarity_result] + [row[0] for row in keyword_result]

    keyword_list = [
        {"text": row[0], "topic": row[1], "subtopic":row[2]}
        for row in keyword_result
    ]

    similarity_list = [
        {"text": row[4], "topic": row[1], "subtopic":row[3]}
        for row in similarity_result
    ]

    combined_dict = {}
    for item in keyword_list + similarity_list:
        if item["text"] not in combined_dict:
            combined_dict[item["text"]] = item  # simpan unik berdasarkan isi teks

    combined_list = list(combined_dict.values())  # hasil akhir sebagai list of dict


    if not combined_list:
        return []

    print("combined search", combined_list)

    # Inisialisasi client Cohere
    co = cohere.ClientV2(api_key="jvvF0hEiBCsJENHbklV7aMPWXF6gxGvt03ifPYYI")

    # Reranking dengan Cohere
    rerank_result = co.rerank(
        model="rerank-v3.5",
        query=question,
        documents=combined_list,
    )

    print("rerank result", rerank_result)

    # Ambil teks produk dan skor relevansi berdasarkan indeks hasil reranking
    reranked_items = [(combined_list[item.index], item.relevance_score) for item in rerank_result.results]
    print("reranked items", reranked_items)

    # Hapus duplikasi dengan mempertahankan skor tertinggi
    unique_reranked_items = {}
    for item, score in reranked_items:
        text_content = item['text']
        # Hanya simpan item dengan skor tertinggi untuk teks yang sama
        if text_content not in unique_reranked_items or unique_reranked_items[text_content][1] < score:
            unique_reranked_items[text_content] = (item, score)

    # Konversi kembali ke list sambil mempertahankan urutan
    final_results = list(unique_reranked_items.values())
    print("final result", final_results)

    return final_results

def build_context_from_results(results):
    # context = "KONTEKS:\n"
    context = ""
    for row in results:
        cid, cdesc, embedd, cktopic = row
        context += f"- Produk {cktopic} memiliki deskripsi: {cdesc}\n"
    return context



def build_context_from_rerank(results):
    print("result", results)
    context = ""
    if not results:
        return context, None  # Kembalikan juga topicquestion sebagai None
    start = 1

    first_desc, first_score, first_topic,firstsubtopic = results[0]
    if first_score <= 0.2:
        return context, None  # Tidak memenuhi syarat, langsung keluar

    context += f"{start}. {first_desc}\n"
    base_score = first_score
    list_topic = [first_topic]  # Mulai dengan topik dari entri pertama
    list_subtopic = [firstsubtopic]
    start += 1

    for desc, score, topic,subtopic in results[1:]:
        if abs(base_score - score) < 0.25:
            context += f"{start}. {desc}\n"
            list_topic.append(topic)
            list_subtopic.append(subtopic)
            start += 1
        else:
            break  # Stop kalau jaraknya lebih dari 0.25

    # Hitung frekuensi tiap topik
    topic_counts = Counter(list_topic)
    total = len(list_topic)

    subtopic_counts = Counter(list_subtopic)
    totalsubtopic = len(list_subtopic)

    # Ambil topik dengan jumlah terbanyak
    most_common_topic, count = topic_counts.most_common(1)[0]
    most_common_subtopic,countsubtopic = subtopic_counts.most_common(1)[0]

    # Logika penentuan topicquestion
    if count == total:
        topicquestion = most_common_topic  # Semua topik sama
    elif count / total >= 0.75:
        topicquestion = most_common_topic  # Mayoritas ≥ 75%
    else:
        topicquestion = None  # Tidak ada mayoritas

    if countsubtopic == totalsubtopic:
        subtopicquestion = most_common_subtopic
    elif countsubtopic / totalsubtopic >= 0.75:
        subtopicquestion = most_common_subtopic
    else:
        subtopicquestion = None 

    print("topicquestion:", topicquestion)
    print("subtopicquestion",subtopicquestion)
    return context, topicquestion, subtopicquestion


def rag_chat(question):
    total_start = time.time()

    hybrid_result = hybrid_search(question)
    print("hybrid result",hybrid_result)
    topicquestion = ""
    subtopic = ""


    # hybrid_context = build_context_from_rerank(hybrid_result)
    hybrid_context,topicquestion,subtopic = build_context_from_rerank([(item['text'], score,item['topic'],item['subtopic']) for item, score in hybrid_result])
    print("topic",topicquestion)
    print("subtopic",subtopic)
    print("final context",hybrid_context)
    # trigrim_srch = trigram_search(question)
    # print("Trigram result",trigrim_srch)

    context_status = "KONTEKS TERSEDIA" if hybrid_context.strip() else "KONTEKS KOSONG"

    if context_status == "KONTEKS KOSONG":
        result = "Halo sobat JRE mohon maaf saya tidak bisa memberikan jawaban mengenai pertanyaan yang kamu berikan ,saya akan mencoba untuk menghubungi admin untuk informasi ini"
        return result,topicquestion,subtopic
    

    llm = Llama (
    model_path = r"D:\Llama-3.1-8B-ArliAI-Indo-Formax-v1.0-Q6_K.gguf",
    n_threads=10,  # jika ingin lebih cepat, sesuaikan dengan jumlah core CPU,
    n_ctx=3000,
    # n_gpu_layers=30,
    n_batch=521,
    verbose=True
    )


    full_context = (
    "Kamu merupakan virtual asistant yang membantu customer dalam menjawab seputar informasi yang berada pada PT Japfa, kamu dapat menjawab setiap pertanyaan dari user dengan mengikuti aturan berikut : \n"
    "1. Jawablah setiap pertanyaan yang diberikan hanya berdasarkan konteks yang diberikan, jangan menggunakan informasi umum yang kamu punyai.\n"
    "Catatan penting dalam memahami konteks usia ayam:\n"
    "- Jika usia ayam disebutkan dalam bulan, maka konversikan menjadi minggu untuk mencocokkannya dengan rentang usia produk.\n"
    "- Gunakan panduan berikut untuk konversi: 1 bulan = 4 minggu, 2 bulan = 8 minggu, dan seterusnya.\n"
    "- Jika usia ayam (dalam minggu hasil konversi) masuk ke dalam rentang usia produk atau melebihi rentang usia produk, maka anggap cocok.\n"
    "2. Jika konteks relevan atau mengandung informasi dari pertanyaan yang diberikan maka jawab pertanyaan berdasarkan konteks yang diberikan, serta jawab dengan awalan kalimat 'Halo Sobat JRE'.\n"
    "3. Jika pengguna meminta daftar, contoh, atau menyebutkan 'apa saja', tetapi tidak ada konteks yang relevan dalam data yang tersedia, maka jangan menjawab atau mengarang jawaban. Jawab hanya jika terdapat konteks yang secara eksplisit relevan.\n"
    "4. Jangan mencampurkan informasi antar konteks, jangan mengambil penjelasan dari luar konteks yang diberikan, jangan mengansumsikan informasi apabila konteks yang ditanyakan di dalam pertanyaan berbeda dengan informasi yang terdapat di dalam konteks.\n"
    "5. Jika tidak ada informasi yang tertera didalam konteks yang diberikan maka jawab dengan alasan mengapa kamu tidak dapat menjawab pertanyaan tersebut serta dengan struktur kalimat 'Halo Sobat JRE mohon maaf saya tidak bisa memberikan jawaban mengenai pertanyaan yang kamu berikan dikarenakan (alasan) saya akan mencoba untuk menghubungi admin untuk informasi ini'. Jangan memberikan informasi umum atau menambahkan informasi apabila memang kamu tidak bisa menjawab pertanyaan tersebut.\n"
    "Berikut merupakan konteks yang diberikan :\n"
    f"{hybrid_context}\n"
)



    print("full_context",full_context)

    # Step 4: Buat prompt dan panggil LLM
    print("Mulai generate jawaban dari LLM...")
    llm_start = time.time()
    response = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": full_context},
            {"role": "user", "content": question}
        ],
        max_tokens=3072,
    )


    
    llm_end = time.time()
    print(f"[WAKTU] LLM response selesai dalam {llm_end - llm_start:.2f} detik")

    total_end = time.time()
    print(f"[TOTAL WAKTU] Semua proses selesai dalam {total_end - total_start:.2f} detik")
    print("response",response["choices"][0]["message"]["content"])
    answer = response["choices"][0]["message"]["content"]

    # llm._sampler.close()
    # llm.close()

    return answer,topicquestion,subtopic


app = Flask(__name__)
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        question = data.get('question')
        username = data.get('username')
        sessionid = data.get('sessionid')

        if not question or not username or not sessionid:
            return jsonify({'error': 'question  username  dan sessionid wajib diisi'}), 400

        print("question:", question)

        # 1. Jalankan RAG
        jawaban, topicquestion,subtopic = rag_chat(question)
        print("topicquestion:", topicquestion)
        print("subtopic",subtopic)

        saran,topicquestion,subtopic = guide_knowledge(question,jawaban,topicquestion,subtopic)

        # if topicquestion == "" and subtopic == "":
        #     saran,topicquestion,subtopic = guide_knowledge(question,jawaban,topicquestion,subtopic)
        
        # insertresponsetodb(sessionid,username,topicquestion,subtopic,question,jawaban,saran)

        # 4. Return response ke user
        return jsonify({
            "answer": jawaban,
            "status":"success"
        })

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({'error': str(e)}), 500
    

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000)
