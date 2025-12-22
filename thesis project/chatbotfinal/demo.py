import streamlit as st
import requests
from sentence_transformers import SentenceTransformer,util
import json
from datetime import datetime
import psycopg2
from llama_cpp import Llama
import uuid  # untuk generate session_id unik


embedding_model = SentenceTransformer("firqaaa/indo-sentence-bert-base")



# Dummy function placeholders (definisikan sesuai implementasi kamu)
# def split_into_trigrams(text):
#     import re
#     # Hilangkan tanda baca dan ubah ke lowercase (opsional)
#     words = re.findall(r'\w+', text.lower())
    
#     # Sliding window 3 kata
#     trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]
#     return trigrams

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




def guide_knowledge(question, answer,userating):
    print("Masuk guideknowledge")
    rating = int(userating)
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
    subtopic = getsubtopic()
    print("sub topic",subtopic)
    formatted_subtopics = "\n".join(f"{i+1}. {sub}" for i, sub in enumerate(subtopic))



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
    if overall_similarity > 0.7 or (1 <= rating <= 3):
        print("Pertanyaan tidak bisa terjawab dengan sempurna atau customer tidak puas terhadap jawaban")
        st.write("Pertanyaan tidak bisa dijawab dengan benar")
        full_context = (
            "Anda adalah asisten virtual yang bertugas membantu admin untuk:\n"
            "- Memberikan saran tentang data/informasi apa yang sebaiknya ditambahkan ke dalam database agar dapat menjawab pertanyaan berikut dengan lebih baik.\n\n"
            "Berikan klasifikasi apakah pertanyaan masuk ke dalam salah satu subtopik berikut ini. "
            "Jika tidak, maka kategorikan ke dalam 'lain-lain'. Berikut daftar subtopik:\n"
            f"{formatted_subtopics}\n\n"
            "Berikanlah juga klasifikasi apakah pertanyaan termasuk kedalam topic apa berdasarkan 3 kategori topik dibawah ini : "
            "1.Product knowledge : Topic pertanyaan mengenai produk "
            "2.Agent knowledge : Topic pertanyaan mengenai sales ,bagaimana cara membeli produk , menanyakan agent di suatu wilayah tertentu"
            "3.FAQ : Pertanyaan lain selain 2 kategori topik diatas"
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

    # 7. Jika jawaban sudah cukup
    elif overall_similarity <= 0.75 : 
        full_context = (
            "Anda adalah asisten virtual yang bertugas membantu admin untuk:\n"
            "- Memberikan saran tentang data/informasi apa yang sebaiknya ditambahkan ke dalam database agar dapat menjawab pertanyaan berikut dengan lebih baik.\n\n"
            "Berikan klasifikasi apakah pertanyaan masuk ke dalam salah satu subtopik berikut ini. "
            "Jika tidak, maka kategorikan ke dalam 'lain-lain'.jangan menerjemahkan sub topic kedalam bahasa indonesia tetap sesuai yang diberikan berdasarkan daftar sub topik nya. Berikut daftar subtopik:\n"
            f"{formatted_subtopics}\n\n"
            "Berikanlah juga klasifikasi apakah pertanyaan termasuk kedalam topik apa berdasarkan 3 kategori topik dibawah ini : "
            "1.Product knowledge : Topic pertanyaan mengenai produk "
            "2.Agent knowledge : Topic pertanyaan mengenai sales ,bagaimana cara membeli produk , menanyakan agent di suatu wilayah tertentu"
            "3.FAQ : Pertanyaan lain selain 2 kategori topik diatas"
            "Jawaban Anda harus diberikan dalam format JSON dengan struktur sebagai berikut:\n\n"
            "{\n"
            "  \"topik\": \"\"\n"
            "  \"sub topik\": \"\"\n"
            "}\n\n"
            f"Konteks:\n"
            f"Pertanyaan: {question}\n"
            f"Jawaban: {answer}\n"
        )

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
        topic = response_json.get("topik","Tidak ada topik")
        subtopic = response_json.get("sub topik","tidak ada sub topik")
    except json.JSONDecodeError:
        print("⚠️ Gagal parsing JSON, fallback ke string biasa")
        saran = raw_response
    return saran,topic,subtopic

def get_connection():
    """Membuat koneksi ke database PostgreSQL dan mengembalikan objek koneksi."""
    
    conn = psycopg2.connect(
        host="43.218.94.232",
        port=5432,
        database="postgres",
        user="postgres",
        password="root",
    )
    return conn


def insertresponsetodb(username, question, answer,userresponse,saran,klasifikasi,topic):
    try:
        conn = get_connection()
        curr = conn.cursor()
        getdate = datetime.now()
        query = """
                INSERT INTO mtlogquestionuser
                (cid, cname, cquestion, canswer,date,cuserating,csuggestion,ctopicquestion,csubtopicquestion) 
                VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s)
                """
        curr.execute(query, ("1", username, question, answer,getdate,userresponse,saran,klasifikasi,topic))
        conn.commit()
        conn.close()
        print("insert berhasil")

    except Exception as e:
        print("error saat insert ke database:", e)
import streamlit as st
import requests

def main():
    st.set_page_config(page_title="Chat LLM Interaktif", page_icon="💬")

    if "step" not in st.session_state:
        st.session_state.step = 1
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = [{"role": "assistant", "content": "Halo! Silakan masukkan username kamu."}]

    # CSS styling
    st.markdown("""
        <style>
        .chat-container {
            display: flex;
            margin-bottom: 10px;
        }
        .chat-bubble {
            padding: 12px 16px;
            border-radius: 20px;
            max-width: 80%;
            word-wrap: break-word;
            font-size: 16px;
        }
        .user-msg {
            background-color: #DCF8C6;
            margin-left: auto;
        }
        .assistant-msg {
            background-color: #F1F0F0;
            margin-right: auto;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>🧠 Tanya Jawab Interaktif</h1>", unsafe_allow_html=True)

    # Tampilkan riwayat chat
    for msg in st.session_state.messages:
        role = msg["role"]
        text = msg["content"]
        css_class = "user-msg" if role == "user" else "assistant-msg"
        st.markdown(
            f'<div class="chat-container"><div class="chat-bubble {css_class}">{text}</div></div>',
            unsafe_allow_html=True
        )

    # Form input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area("Ketik di sini...", key="user_input", height=80)
        submitted = st.form_submit_button("Kirim")

    if submitted and user_input.strip():
        user_input = user_input.strip()
        st.session_state.messages.append({"role": "user", "content": user_input})

        if st.session_state.step == 1:
            st.session_state.username = user_input
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"Halo {user_input}, selamat datang di chatbot knowledge. Mohon masukkan pertanyaanmu di sini."
            })
            st.session_state.step = 2
            st.rerun()

        elif st.session_state.step == 2:
            st.session_state.question = user_input
            with st.spinner("Menghubungi API untuk menjawab..."):
                try:
                    response = requests.post("http://43.218.94.232:5000/ask", json={
                        "username": st.session_state.username,
                        "userid":"c12345",
                        "sessionid": st.session_state.session_id,
                        "question": st.session_state.question
                    })
                    data = response.json()
                    answer = data.get("answer", "Jawaban tidak tersedia.")
                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"Gagal menghubungi API: {e}"})

            st.session_state.messages.append({"role": "assistant", "content": "Apakah ada pertanyaan lain? (ya/tidak)"})
            st.session_state.step = 3
            st.rerun()

        elif st.session_state.step == 3:
            if user_input.lower() == "ya":
                st.session_state.messages.append({"role": "assistant", "content": "Silakan tuliskan pertanyaan baru kamu."})
                st.session_state.step = 2
                st.rerun()
            elif user_input.lower() == "tidak":
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": "Terima kasih sudah menghubungi kami! 🙏 Apakah kamu bersedia memberikan saran untuk kami?"
                })
                st.session_state.step = 4
                st.rerun()
            else:
                st.session_state.messages.append({"role": "assistant", "content": "Mohon jawab dengan 'ya' atau 'tidak'."})
                st.rerun()

        elif st.session_state.step == 4:
            st.session_state.saran = user_input
            with st.spinner("Mengirim saran..."):
                try:
                    response = requests.post("http://43.218.94.232:5000/ask", json={
                        "sessionid": st.session_state.session_id,
                        "suggestion": st.session_state.saran
                    })
                    if response.status_code == 200:
                        st.session_state.messages.append({"role": "assistant", "content": "Saran berhasil disimpan."})
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "Gagal menyimpan saran."})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"Gagal kirim saran: {e}"})

            st.session_state.messages.append({"role": "assistant", "content": "Silakan beri rating dari 1 (tidak puas) sampai 5 (sangat puas)."})
            st.session_state.step = 5
            st.rerun()

        elif st.session_state.step == 5:
            st.session_state.rating = user_input
            with st.spinner("Mengirim rating..."):
                try:
                    response = requests.post("http://43.218.94.232:5000/ask", json={
                        "sessionid": st.session_state.session_id,
                        "rating": st.session_state.rating
                    })
                    if response.status_code == 200:
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": "Terima kasih atas rating Anda! 🙏 Sampai jumpa lagi."
                        })
                    else:
                        st.session_state.messages.append({"role": "assistant", "content": "Gagal menyimpan rating."})
                except Exception as e:
                    st.session_state.messages.append({"role": "assistant", "content": f"Gagal kirim rating: {e}"})
            st.session_state.step = 6
            st.rerun()


if __name__ == "__main__":
    main()