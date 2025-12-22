from email.policy import default
from string import punctuation
import token
import streamlit as st
from db_connection import get_connection
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from customfield import main as customfield_page
# from listknowledgenew import listknowledge_page as listknowledgepage
import numpy as np
import re
import nltk
from nltk import sent_tokenize
import os
import psycopg2



# Koneksi ke database
# conn = get_connection()
conn = psycopg2.connect(
dbname="skripsi",
user="postgres",
password="root",
host="localhost"
)   
# conn = psycopg2.connect(
#         host="43.218.94.232",
#         port=5432,
#         database="postgres",
#         user="postgres",
#         password="root"
# )
curr = conn.cursor()
def chunk_with_overlap(text, token_limit=450, overlap=50):
    tokenizer = AutoTokenizer.from_pretrained("firqaaa/indo-sentence-bert-base")
    words = text.strip().split()
    chunks = []
    i = 0

    while i < len(words):
        current_chunk = []
        current_token_count = 0
        j = i

        # Tambah kata sampai mencapai token limit
        while j < len(words):
            word = words[j]
            token_count = len(tokenizer.tokenize(word))

            if current_token_count + token_count > token_limit:
                break

            current_chunk.append(word)
            current_token_count += token_count
            j += 1

        chunks.append(" ".join(current_chunk))

        # Pindah index untuk next chunk dengan overlap
        if j == len(words):  # kalau udah sampai akhir
            break

        # Hitung mundur kata yang membentuk overlap token
        overlap_words = []
        token_back = 0
        k = len(current_chunk) - 1
        while k >= 0 and token_back < overlap:
            w = current_chunk[k]
            token_back += len(tokenizer.tokenize(w))
            overlap_words.insert(0, w)
            k -= 1

        i = j - len(overlap_words)

    return chunks

def gettemplatetopic(filter_option):
    print("filter option",filter_option)
    query = "SELECT ctopictemplatefield FROM mtlistfield WHERE ctopicfield = %s"
    
    try:
        # Ganti dengan detail koneksi PostgreSQL kamu
        conn = psycopg2.connect(
            dbname="skripsi",
            user="postgres",
            password="root",
            host="localhost"
        )   
        # conn = psycopg2.connect(
        #     host="43.218.94.232",
        #     port=5432,
        #     database="postgres",
        #     user="postgres",
        #     password="root"
        # )
        cur = conn.cursor()
        cur.execute(query, (filter_option,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            return result[0]  # ambil hasil template-nya saja
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

def chunking_optimalization(sentences, topic):
    tokenizer = AutoTokenizer.from_pretrained("firqaaa/indo-sentence-bert-base")
    chunklistsentence = []
    chunktemp = ""
    token_limit = 500
    print("sentences",sentences)
    for sentence in sentences:
        if topic == "Product Knowledge" or topic == "Agent Knowledge":
            tokens = tokenizer.tokenize(chunktemp + sentence)
            if len(tokens) <= token_limit:
                    print("masuk if pk")
                    print("chunktemp",chunktemp)
                    print("sentence",sentence)
                    chunktemp += sentence
            else:
                print("masuk else pk")
                if chunktemp:
                    chunklistsentence.append(chunktemp.strip())
                    chunktemp = ""


                sentence_tokens = tokenizer.tokenize(sentence)

                if len(sentence_tokens) > token_limit:
                    print("Masuk sini")
                    # sub_sentences = sentence.split(".")
                    sub_sentences = sent_tokenize(sentence)
                    sub_temp = ""
                    for sub in sub_sentences:
                        sub = sub.strip()
                        subsentencetoken = tokenizer.tokenize(sub)
                        if not sub:
                            continue
                        sub_tokens = tokenizer.tokenize(sub_temp + sub)
                        if len(sub_tokens) <= token_limit:
                            sub_temp += sub
                            print("sub temp",sub_temp)
                        else:
                            sisatokens = token_limit - len(tokenizer.tokenize(sub_temp))
                            print("Sisa tokens",sisatokens)
                            print("Panjang subsentencetoken",len(subsentencetoken))
                            if len(subsentencetoken) > sisatokens and sisatokens > 50 :
                                print("ada sub sentence yang panjangnya melebihi sisa token")
                                print("subtemp",sub_temp)
                                print("sub",sub)
                                token_limits = sisatokens
                            
                                lensub = len(tokenizer.tokenize(sub))
                                if 500 <= lensub <= 1000 and  sisatokens >= 500 :
                                    if lensub % 2 == 0:
                                        token_limits = lensub / 2
                                    elif lensub % 2  == 1:
                                        token_limits = (lensub / 2) + 1
                                
                                
                                chunks = chunk_with_overlap(sub,token_limit=token_limits,overlap=0)
                                print("chunks",chunks)
                                for i,subchunksentence  in enumerate(chunks):
                                    token_count = len(tokenizer.tokenize(subchunksentence))
                                    print(f"\nChunk hasil overlap {i+1} Token :{token_count} :\n{subchunksentence}")
                                    if i == 0:
                                        chunklistsentence.append((sub_temp + subchunksentence))
                                    elif i == len(chunks) - 1:
                                        # sub_temp = subchunksentence
                                        chunktemp = subchunksentence
                                    else:
                                        chunklistsentence.append(subchunksentence)
                                sub_temp = ""
                            else:
                                print("masuk else else",sub_temp)
                                print("Masuk sub",sub)
                                if sub_temp:
                                    chunklistsentence.append(f"{sub_temp.strip()}")
                                sub_temp = sub
                                # chunktemp = sub
                        if sub_temp:
                            chunklistsentence.append( f"{sub_temp.strip()}")
                            # chunktemp = sub_temp
                else:
                    print("masuk sentence",sentence)
                    chunklistsentence.append(sentence.strip())


        elif topic == "FAQ":
            print("ini FAQ")
            sentence_tokens = tokenizer.tokenize(sentence)
            # Jika satu kalimat melebihi token_limit, simpan sebagai chunk sendiri
            # if len(sentence_tokens) > token_limit:
            #     print("satu kalimat melebihi token limit",sentence)
            #     chunklistsentence.append(sentence.strip())
            #     continue

            # Coba gabungkan dengan chunk sebelumnya
            combined = chunktemp + " " + sentence if chunktemp else sentence
            combined_tokens = tokenizer.tokenize(combined)

            if len(combined_tokens) <= token_limit:
                chunktemp = combined
                print("masuk if")
                print("Panjang chunk",len(tokenizer.tokenize(chunktemp)))
                print("Chunk",chunktemp)

            else:
                print("masuk else")
                lensubtemp = len(tokenizer.tokenize(chunktemp))
                print("Panjang chunk",lensubtemp)
                print("chunktemp",chunktemp)
                print("sentence",sentence)
                lensentencetoken = len(tokenizer.tokenize(sentence))

                print("sentence",sentence)
                print("panjang sentence",lensentencetoken)
                print("combined",len(combined_tokens))
                sisatokens = token_limit - lensubtemp
                resultchunksplit = []
                if lensentencetoken > token_limit:
                    if sisatokens >= 500:
                        print("sentence melebihi token_limit harus dipisah")
                        resultchunksplit = chunk_with_overlap(sentence,token_limit=token_limit,overlap = 20)
                        print("resultchunksplit",resultchunksplit)
                    elif 100 < sisatokens < 500:
                        resultchunksplit = chunk_with_overlap(sentence,token_limit=sisatokens,overlap = 10 )
                    subchunk = ""
                    for idx,chunk in enumerate(resultchunksplit):
                        if idx == 0:
                            chunktemp += chunk
                            chunklistsentence.append(chunktemp.strip())
                        elif idx == len(resultchunksplit) - 1:
                            chunktemp = chunk
                        else:
                            if len(tokenizer.tokenize(chunk)) < token_limit:
                                subchunk += "" + chunk
                            else:
                                chunklistsentence.append(chunk)
                            if subchunk:
                                chunklistsentence.append(subchunk)
                else:
                    chunklistsentence.append(chunktemp.strip())
                    chunktemp = sentence  # mulai chunk baru
    if chunktemp:
        chunklistsentence.append(chunktemp.strip()) 
    return chunklistsentence
            
def chunking_data_process(cknowledgetopic,cknowledgeinformation):
    try:
        # Load tokenizer
        tokenizer = AutoTokenizer.from_pretrained("firqaaa/indo-sentence-bert-base")
        tokens = tokenizer.tokenize(cknowledgeinformation)
        print("Tokens full text:", len(tokens))

        token_limit = 500
        sentences = []
        # Step 1: Preprocess berdasarkan type
        if cknowledgetopic == "FAQ":
            sentences = sent_tokenize(cknowledgeinformation)
        elif cknowledgetopic == "Product Knowledge":
            pattern = r"(?=(\b(?:Nama produk|Katalog produk.*?|Fungsi / tujuan produk.*?|Jenis produk.*?|Jenis Pakan ternak.*?|Nama brand produk.*?|Kandungan yang terdapat didalam produk.*?|Deskripsi umum produk.*?|Kelemahan kelebihan produk.*?|Informasi lanjutan produk.*?)\s*:\s*))"
            sections = re.split(pattern, cknowledgeinformation)
            for i in range(1, len(sections), 2):
                value = sections[i + 1].strip()
                sentences.append(value)

            print("sentence product knowledge",sentences)
            
        elif cknowledgetopic == "Agent Knowledge":
            pattern = r"(?=(\b(?:nama agent|lokasi|sub agent)\s*:\s*))"
            sections = re.split(pattern, cknowledgeinformation, flags=re.IGNORECASE)
            for i in range(1, len(sections), 2):
                label = sections[i].strip()
                value = sections[i + 1].strip()
                stop = re.search(pattern, value, flags=re.IGNORECASE)
                value = value[:stop.start()] if stop else value
                sentences.append(f"{label} {value.strip()}")

        # chunk optimalization
        result = chunking_optimalization(sentences,cknowledgetopic)
        start = 1
        for i in result:
            lentokens = len(tokenizer.tokenize(i))
            print(f"Panjang token ke {start} : {lentokens} ")
            print(f"chunks {start} : {i} ")
            start = start + 1

    except Exception as e:
        print(f"Terjadi kesalahan saat memproses informasi : {e}")
    return result


# listknowledgenew.py
def save_data(cknowledgetopic, cknowledgeinformation, cknowledgetopicinformation, cknowledgesubtopic, sessiongetstatus):
    try:
        conn = get_connection()  # Ambil koneksi, tapi JANGAN ditutup di sini
        embedding_model = SentenceTransformer("firqaaa/indo-sentence-bert-base")
        tokenizer = AutoTokenizer.from_pretrained("firqaaa/indo-sentence-bert-base")
        token_limit = 500

        sentences = sent_tokenize(cknowledgeinformation)
        print("sentences punctuation result", sentences)

        # Langkah 2: Chunking
        chunks = []
        if len(tokenizer.tokenize(cknowledgeinformation)) > token_limit:
            print("text harus dilakukan proses chunking")
            chunks = chunking_data_process(cknowledgetopic, cknowledgeinformation)
        else:
            chunks.append(cknowledgeinformation)

        embeddings = embedding_model.encode(chunks[0]).tolist()  # Ambil hanya 1 chunk untuk saat ini

        with conn.cursor() as curr:
            if sessiongetstatus == "addnewknowledge":
                print("masuk insert",cknowledgeinformation)
                query = """
                    INSERT INTO mtknowledgebase 
                    (cknowledgetopic,cknowledgetopicinformation,cknowledgesubtopic,cknowledgeinformation,cknowledgembedding) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                curr.execute(query, (cknowledgetopic,cknowledgetopicinformation,cknowledgesubtopic,cknowledgeinformation, embeddings))

            elif sessiongetstatus == "editproduct":
                print("masuk edit",cknowledgeinformation)
                # cid = st.session_state.get("selected_data")["id"][0]
                cid = st.session_state.selected_data.get("id")
                cid = int(cid) if cid is not None else None
                print("cid", cid)

                query = """
                    UPDATE mtknowledgebase
                    SET 
                        cknowledgeinformation = %s,
                        cknowledgembedding = %s,
                        cknowledgetopicinformation = %s,
                        cknowledgesubtopic = %s
                    WHERE 
                        cid = %s
                """
                curr.execute(query, (cknowledgeinformation, embeddings, cknowledgetopicinformation, cknowledgesubtopic, cid))

            conn.commit()  # Tetap commit ya

    except Exception as e:
        conn.rollback()
        st.error(f"Terjadi kesalahan: {e}")

def getsubtopic ():
    try:
        conn = get_connection()
        with conn.cursor() as curr:
            curr.execute("SELECT DISTINCT cknowledgesubtopic FROM mtknowledgebase")
            subtopics = [row[0] for row in curr.fetchall()]
        return subtopics
    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil subtopik: {e}")
        return []

def gettemplatefield(filter_option):
    print("filter option",filter_option)
    query = "SELECT clabelfield FROM mtlistfield WHERE ctopicfield = %s"
    
    try:
        # Ganti dengan detail koneksi PostgreSQL kamu
        conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
        )   
        # conn = psycopg2.connect(
        #     host="43.218.94.232",
        #     port=5432,
        #     database="postgres",
        #     user="postgres",
        #     password="root"

        # )
        cur = conn.cursor()
        cur.execute(query, (filter_option,))
        result = cur.fetchone()

        cur.close()
        conn.close()

        if result:
            return result[0]  # ambil hasil template-nya saja
        else:
            return None
    except Exception as e:
        print("Error:", e)
        return None

def getopic():
    try:
        conn = get_connection()
        with conn.cursor() as curr:
            curr.execute("SELECT DISTINCT cknowledgetopic FROM mtknowledgebase")
            topics = [row[0] for row in curr.fetchall()]
        return topics
    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil topik: {e}")
        return []


def main():
    sessiongetstatus = st.session_state.get("status")
    print("sessiongetstatus", sessiongetstatus)
    if "statuspage" not in st.session_state:
        st.session_state.statuspage = "mainpage"
    if st.session_state.statuspage  == "customfield":
        print("Masuk ke custom field")
        # st.session_state.reset_session = False
        customfield_page()
        return;
    if st.session_state.statuspage == "mainpage":
        if sessiongetstatus == "addnewknowledge":
            st.title("Add your new knowledge")
        if sessiongetstatus == "editproduct":
            st.title("Edit your product knowledges")
            sessiongetedititem = st.session_state.get("selected_data","")
            # st.write("sessiongetedititem",sessiongetedititem)
        cknowledgeinformation = ()
        cknowledgetopicinformation = ""
        cknowledgesubtopic = ""

        default_topic = ["FAQ", "Product Knowledge","Agent Knowledge"]
        topic = getopic()
        for t in default_topic:
            if t not in topic:
                topic.append(t)

        options = topic + ["➕ Buat Topik Baru"]
        if "cknowledgesubtopic" not in st.session_state:
            st.session_state["cknowledgesubtopic"] = ""
        # options = options + ["➕ Buat Topik Baru"]
        # cknowledgetype = st.selectbox("Pilih topik knowledge yang akan dimasukkan", options)
        default_type = options.index(sessiongetedititem["type"]) if sessiongetstatus == "editproduct" and sessiongetedititem else 0
        default_subtopic = sessiongetedititem["subtopic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

        cknowledgetopic = st.selectbox("Pilih topik knowledge yang akan dimasukkan", options, index=default_type)
        getopicfaq = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
        is_new_topic = cknowledgetopic == "➕ Buat Topik Baru"

        if is_new_topic:
            cknowledgetopic = st.text_input("Masukkan topik baru:")

            templatetopic = ["FAQ", "Product Knowledge", "Agent Knowledge"]

            subtopics = getsubtopic()  # Ambil dari fungsi yang sudah dibuat
            print("subtopics", subtopics)
            # Tambahkan opsi untuk buat baru
            subtopics_with_new = subtopics + ["➕ Buat Sub Topik Baru"]
            if default_subtopic  in subtopics_with_new:
                default_index = subtopics_with_new.index(default_subtopic)
            else:   
                default_index = 0

            # Dropdown pilih subtopik
            cknowledgesubtopic = st.selectbox(
                "Pilih jenis subtopik dari informasi umum:",
                subtopics_with_new,
                index = default_index,
            )
            # Jika pilih opsi buat baru
            if cknowledgesubtopic == "➕ Buat Sub Topik Baru":
                new_subtopic = st.text_input("Masukkan sub topik baru:")
                if new_subtopic.strip() == "":
                    st.warning("Sub topik tidak boleh kosong.")
                else:
                    # Tambahkan ke list (atau simpan ke DB)
                    subtopics.append(new_subtopic.strip())
                    st.success(f"Sub topik '{new_subtopic.strip()}' berhasil ditambahkan!")
                    st.session_state.cknowledgesubtopic = new_subtopic.strip()
                    # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan subtopik baru ke dropdown
            else:
                st.write(f"Sub topik terpilih: {cknowledgesubtopic}")
                st.session_state.cknowledgesubtopic = cknowledgesubtopic

            cknowledgesubtopic = st.session_state.cknowledgesubtopic


            cknowledgetopictemplate = st.selectbox(
                "Pilih jenis template",
                templatetopic,
            )

            customfield = st.button("Custom Field")
            if customfield:
                st.session_state.cknowledgetopictemplate = cknowledgetopictemplate
                st.session_state.cknowledgesubtopic = cknowledgesubtopic
                st.session_state.cknowledgetopic = cknowledgetopic
                st.session_state.statuspage = "customfield"
                print("test",cknowledgetopictemplate, cknowledgesubtopic, cknowledgetopic)
                st.rerun()

            
            # cknowledgesubtopic = st.text_input("Masukkan sub topik baru:")
            # cknowledgetopicinformation = st.text_input("Masukkan Judul informasi  mengenai topik baru", value=getopicfaq)
            # cknowledgeinformation = st.text_area("Masukkan informasi mengenai topik baru", value=getopicfaq)
            # if cknowledgetopicinformation.strip() == "":
            #     st.warning("Topik tidak boleh kosong.")
            # else:
            #     # Tambahkan ke list (atau simpan ke DB)
            #     options.append(cknowledgetopicinformation.strip())
            #     st.success(f"Topik '{cknowledgetopicinformation.strip()}' berhasil ditambahkan!")
            #     st.session_state.cknowledgetopic = cknowledgetopicinformation.strip()
            #     print("Acknowledgetopic", st.session_state.cknowledgetopic)
                # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan topik baru ke dropdown
        
        elif cknowledgetopic == "FAQ":
            st.subheader("📝 Informasi Umum")
            default_topicinformation = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            default_info = sessiongetedititem["information"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            default_subtopic = sessiongetedititem["subtopic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

            # cknowledgesubtopic = st.text_input("Masukan jenis subtopik dari informasi umum (contoh apakah termasuk informasi budidaya ,Aplikasi order pakan ,member JRC ,dll)",value = default_subtopic)

            # Daftar sub topik yang tersedia (bisa dari DB / session / list)
            # subtopics = ["Informasi Budidaya", "Aplikasi Order Pakan", "Member JRC"]
            subtopics = getsubtopic()  # Ambil dari fungsi yang sudah dibuat
            print("subtopics", subtopics)
            # Tambahkan opsi untuk buat baru
            subtopics_with_new = subtopics + ["➕ Buat Sub Topik Baru"]
            if default_subtopic  in subtopics_with_new:
                default_index = subtopics_with_new.index(default_subtopic)
            else:   
                default_index = 0

            # Dropdown pilih subtopik
            cknowledgesubtopic = st.selectbox(
                "Pilih jenis subtopik dari informasi umum:",
                subtopics_with_new,
                index = default_index,
            )
            # Jika pilih opsi buat baru
            if cknowledgesubtopic == "➕ Buat Sub Topik Baru":
                new_subtopic = st.text_input("Masukkan sub topik baru:")
                if new_subtopic.strip() == "":
                    st.warning("Sub topik tidak boleh kosong.")
                else:
                    # Tambahkan ke list (atau simpan ke DB)
                    subtopics.append(new_subtopic.strip())
                    st.success(f"Sub topik '{new_subtopic.strip()}' berhasil ditambahkan!")
                    st.session_state.cknowledgesubtopic = new_subtopic.strip()
                    # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan subtopik baru ke dropdown
            else:
                st.write(f"Sub topik terpilih: {cknowledgesubtopic}")
                st.session_state.cknowledgesubtopic = cknowledgesubtopic

            cknowledgesubtopic = st.session_state.cknowledgesubtopic

            cknowledgetopicinformation = st.text_input("Masukkan topik informasi umum atau contoh pertanyaan seputar FAQ yang ingin dijawab oleh sistem", value=default_topicinformation)
            cinformation = st.text_area("Masukan data /isi  dari informasi umum", value=default_info)
            cknowledgeinformation = (
                f"Topik atau contoh pertanyaan : {cknowledgetopicinformation}.\n"
                f"informasi : {cinformation}.\n"
            ) 

        elif cknowledgetopic == "Product Knowledge":
            # Inisialisasi session state untuk multi-step form

            getnamaproduct = sessiongetedititem["nama produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getkatalogproduct = sessiongetedititem["Katalog produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getjenisproduct = sessiongetedititem["Jenis produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getbrandproduct = sessiongetedititem["Brand produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getfungsiproduct = sessiongetedititem["Fungsi produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getkelemahankelebihanproduct = sessiongetedititem["Kelemahan kelebihan produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getkandunganproduct = sessiongetedititem["Kandungan produk"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            getinfolainproduct = sessiongetedititem["info lain"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""


            
            if "product_section" not in st.session_state:
                st.session_state.product_section = 1

        # SECTION 1: Form awal
            if st.session_state.product_section == 1:
                st.subheader("📝 Informasi Produk - Bagian 1")
                # cnama = st.text_input("Masukan nama pakan produk",value = getnamaproduct)

                col1, col2 = st.columns(2)
                with col1:
                    cnama = st.text_input("Masukan nama produk",value = getnamaproduct)
                    ckatalog = st.text_input("Masukan katalog produk",value = getkatalogproduct)
                    cbrand = st.text_input("Masukan brand produk",value = getbrandproduct)

                with col2:
                    options = ["Pakan Ternak", "Produk lain"]
                    cjenisproduk = st.selectbox("Pilih Jenis Produk", options, index=default_type)
                    ckegunaan = st.text_input("Masukan kegunaan produk (untuk hewan/usia berapa)",value = getfungsiproduct)
                    # cjenis = st.text_input("Masukan jenis pakan produk",value = getjenisproduct)
                    if cjenisproduk == "Pakan Ternak":
                        cjenis = st.text_input("Masukan jenis pakan ternak",value = getjenisproduct)
                    elif cjenisproduk == "Produk lain":
                        cjenis = st.text_input("Beri keterangan jenis produk lain (Obat obatan ,vitamin,dll)",value = getjenisproduct)

                        
                

                if st.button("Next ➡️", use_container_width=True):
                    # Simpan input sementara ke session_state
                    st.session_state.cnama = cnama
                    st.session_state.ckatalog = ckatalog
                    st.session_state.cbrand = cbrand
                    st.session_state.ckegunaan = ckegunaan
                    st.session_state.cjenisproduk = cjenisproduk
                    st.session_state.cjenis = cjenis
                    st.session_state.product_section = 2
                    st.write(st.session_state.cjenisproduk)
                    st.rerun()

        # SECTION 2: Form lanjutan
            elif st.session_state.product_section == 2:
                st.write(st.session_state.cjenisproduk)
                st.subheader("📝 Informasi Produk - Bagian 2")
                cplusminus = st.text_area("Masukan kelemahan dan kelebihan produk",value = getkelemahankelebihanproduct)
                ckandungan = st.text_area("Masukan kandungan produk",value = getkandunganproduct)
                cinformasilain = st.text_area("Masukan informasi lain / tambahan mengenai produk.",value = getinfolainproduct)

                # Rekonstruksi topic dan information untuk disimpan
                cknowledgetopicinformation = st.session_state.cnama
                cknowledgesubtopic = ""
                # cknowledgeinformation = (
                #     f"Katalog produk {st.session_state.cnama} : {st.session_state.ckatalog} \n"
                #     f"Fungsi / tujuan produk : {st.session_state.ckegunaan} \n"
                #     f"Jenis produk : {st.session_state.cjenis}\n"
                #     f"Nama brand produk : {st.session_state.cbrand}\n"
                #     f"Kandungan yang terdapat didalam produk : {ckandungan}\n"
                #     f"Kelemahan kelebihan produk : {cplusminus}\n"
                #     f"Informasi lain produk : {cinformasilain}\n"
                # )
                product_info_parts = []
                if st.session_state.cnama.strip():
                    product_info_parts.append(f"Nama produk  : {st.session_state.cnama}.")
                if st.session_state.ckatalog.strip():
                    product_info_parts.append(f"Katalog produk {st.session_state.cnama}: {st.session_state.ckatalog}.")
                if st.session_state.ckegunaan.strip():
                    product_info_parts.append(f"Fungsi / tujuan produk {st.session_state.cnama} : {st.session_state.ckegunaan}.")
                if st.session_state.cjenisproduk:
                    product_info_parts.append(f"Jenis produk {st.session_state.cnama} : {st.session_state.cjenisproduk}.")
                if st.session_state.cjenisproduk == "Pakan Ternak":
                    product_info_parts.append(f"Jenis / bentuk Pakan ternak produk {st.session_state.cnama} : {st.session_state.cjenis}.")
                    cknowledgesubtopic = st.session_state.cjenisproduk
                if st.session_state.cjenisproduk == "Produk lain":
                    product_info_parts.append(f"Jenis produk lain {st.session_state.cnama} : {st.session_state.cjenis}.")
                    # cknowledgesubtopic = st.session_state.cjenisproduk + st.session_state.cjenis
                    cknowledgesubtopic = st.session_state.cjenisproduk + " (" + st.session_state.cjenis + ")"

                # if st.session_state.cjenis.strip():
                #     product_info_parts.append(f"Jenis produk : {st.session_state.cjenis}")
                if st.session_state.cbrand.strip():
                    product_info_parts.append(f"Nama brand produk {st.session_state.cnama}  : {st.session_state.cbrand}.")
                if ckandungan.strip():
                    product_info_parts.append(f"Kandungan yang terdapat didalam produk {st.session_state.cnama} : {ckandungan}.")
                if cplusminus.strip():
                    product_info_parts.append(f"Kelemahan kelebihan produk {st.session_state.cnama}  : {cplusminus}.")
                if cinformasilain.strip():
                    product_info_parts.append(f"Informasi lain produk {st.session_state.cnama} : {cinformasilain}.")
                

            # Gabungkan semua bagian menjadi satu string informasi
                print("product_info_parts",product_info_parts)
                cknowledgeinformation = "\n".join(product_info_parts)
                print("cknowledgeinformation",cknowledgeinformation)
                

                # Simpan variabel ini agar bisa diakses tombol Save
                st.session_state.cknowledgetopicinformation = cknowledgetopicinformation
                st.session_state.cknowledgeinformation = cknowledgeinformation
                st.session_state.cknowledgesubtopic = cknowledgesubtopic

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("⬅️ Kembali", use_container_width=True):
                        st.session_state.product_section = 1

        elif cknowledgetopic == "Agent Knowledge":
                
                st.subheader("📝 Agent Knowledge")
                default_topic = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

                getnamagent = sessiongetedititem["nama agent"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                getlokasi = sessiongetedititem["lokasi"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                getsubagent = sessiongetedititem["sub agent"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                print("default topic",default_topic)
        
                cknowledgetopicinformation = st.text_input("Masukan nama owner", value=getnamagent)
                cknowledgesubtopic = "Agent"
                cknowledgeareaagent = st.text_area("Masukan area kawasan agent", value=getlokasi)
                cknowledgesubagent = st.text_input("Masukkan nama sub agent", value=getsubagent)
                cknowledgeinformation = (
                    f"Anda dapat membeli pakan ternak  melalui agent serta sub agent berikut :  "
                    f"nama agent : {cknowledgetopicinformation}\n" 
                    f"lokasi     : {cknowledgeareaagent}\n"
                    f"sub agent  : {cknowledgesubagent}\n"
                )
            
            
                # cknowledgetopic = st.text_input("Masukkan topik seputar agent knowledge")
                # cknowledgeinformation = st.text_area("Masukkan data dari agent knowledge")
        else:
            print("cknowledgetopic masuk else sinii", cknowledgetopic)
            # print("sessiongetedititem",sessiongetedititem)
            getemplatetopic = gettemplatetopic(cknowledgetopic)
            print("getemplate topic awal",getemplatetopic)
            if getemplatetopic == "FAQ":
                sessiongetfieldtitle = st.session_state.get("selected_field","")
                # print("sessiongetfieldtitle",sessiongetfieldtitle)
                getemplatetopic = ""
                field1_title = ""
                field2_title = ""
                st.session_state.cfield7 = ""
                if sessiongetstatus == "editproduct":
                    getemplatetopic = gettemplatetopic(sessiongetedititem['type'])
                    field1_title = sessiongetfieldtitle['field1_title']
                    field2_title = sessiongetfieldtitle['field2_title']
                elif sessiongetstatus == "addnewknowledge":
                    getemplatetopic = gettemplatetopic(cknowledgetopic)
                    getfieldtemplate = gettemplatefield(cknowledgetopic)
                    fields = re.findall(r'"(.*?)"', getfieldtemplate)
                    # fields = re.findall(r'\w+', getfieldtemplate)  # hasil: ['Tanggal', 'Nama']
                    print("fields",fields)
                    field1_title = fields[0]
                    field2_title = fields[1]
                    print("field1_title",field1_title)
                    # print("get field template add product",getfieldtemplate[])
                print("getemplatetopic test",getemplatetopic)
                if getemplatetopic == "FAQ":
                    default_topicinformation = sessiongetedititem['topic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                    default_subtopic = sessiongetedititem['subtopic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                    default_field1_val = sessiongetedititem['field1_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                    default_field2_val = sessiongetedititem['field2_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                    subtopics = getsubtopic()  # Ambil dari fungsi yang sudah dibuat
                    print("subtopics", subtopics)
                    # Tambahkan opsi untuk buat baru
                    subtopics_with_new = subtopics + ["➕ Buat Sub Topik Baru"]
                    if default_subtopic  in subtopics_with_new:
                        default_index = subtopics_with_new.index(default_subtopic)
                    else:   
                        default_index = 0

                    # Dropdown pilih subtopik
                    cknowledgesubtopic = st.selectbox(
                        "Pilih jenis subtopik dari informasi umum:",
                        subtopics_with_new,
                        index = default_index,
                    )
                    # Jika pilih opsi buat baru
                    if cknowledgesubtopic == "➕ Buat Sub Topik Baru":
                        new_subtopic = st.text_input("Masukkan sub topik baru:")
                        if new_subtopic.strip() == "":
                            st.warning("Sub topik tidak boleh kosong.")
                        else:
                            # Tambahkan ke list (atau simpan ke DB)
                            subtopics.append(new_subtopic.strip())
                            st.success(f"Sub topik '{new_subtopic.strip()}' berhasil ditambahkan!")
                            st.session_state.cknowledgesubtopic = new_subtopic.strip()
                            # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan subtopik baru ke dropdown
                    else:
                        st.write(f"Sub topik terpilih: {cknowledgesubtopic}")
                        st.session_state.cknowledgesubtopic = cknowledgesubtopic
                    cknowledgesubtopic = st.session_state.cknowledgesubtopic

                    cfield1 = st.text_input(field1_title,value = default_field1_val)
                    cfield2 = st.text_input(field2_title,value = default_field2_val)
                    cknowledgetopicinformation = cknowledgetopic
                    cknowledgeinformation = (
                    f"{field1_title} : {cfield1}\n"
                    f"{field2_title} : {cfield2}"
                    )
            elif getemplatetopic == "Agent Knowledge":
                print("Agent Knowledge masuk sini")
                sessiongetfieldtitle = st.session_state.get("selected_field","")
                field1_title,field2_title,field3_title = "","",""
                if sessiongetstatus == "addnewknowledge":    
                    getfieldtemplate = gettemplatefield(cknowledgetopic)
                    print("getfieldtemplate",getfieldtemplate)
                    # fields = re.findall(r'"(.*?)"', getfieldtemplate)
                    fields = re.findall(r'"(.*?)"', getfieldtemplate)
                    print("fields",fields)
                    field1_title = fields[0]
                    field2_title = fields[1]
                    field3_title = fields[2]
                elif sessiongetstatus == "editproduct":
                    getemplatetopic = gettemplatetopic(sessiongetedititem['type'])
                    field1_title = sessiongetfieldtitle['field1_title']
                    field2_title = sessiongetfieldtitle['field2_title']
                    field3_title = sessiongetfieldtitle['field3_title']
                default_topicinformation = sessiongetedititem['topic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_subtopic = sessiongetedititem['subtopic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field1_val = sessiongetedititem['field1_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field2_val = sessiongetedititem['field2_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field3_val = sessiongetedititem['field3_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                subtopics = getsubtopic()  # Ambil dari fungsi yang sudah dibuat
                print("subtopics", subtopics)
                # Tambahkan opsi untuk buat baru
                subtopics_with_new = subtopics + ["➕ Buat Sub Topik Baru"]
                if default_subtopic  in subtopics_with_new:
                    default_index = subtopics_with_new.index(default_subtopic)
                else:   
                    default_index = 0

                # Dropdown pilih subtopik
                cknowledgesubtopic = st.selectbox(
                    "Pilih jenis subtopik dari informasi umum:",
                    subtopics_with_new,
                    index = default_index,
                )
                # Jika pilih opsi buat baru
                if cknowledgesubtopic == "➕ Buat Sub Topik Baru":
                    new_subtopic = st.text_input("Masukkan sub topik baru:")
                    if new_subtopic.strip() == "":
                        st.warning("Sub topik tidak boleh kosong.")
                    else:
                        # Tambahkan ke list (atau simpan ke DB)
                        subtopics.append(new_subtopic.strip())
                        st.success(f"Sub topik '{new_subtopic.strip()}' berhasil ditambahkan!")
                        st.session_state.cknowledgesubtopic = new_subtopic.strip()
                        # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan subtopik baru ke dropdown
                else:
                    st.write(f"Sub topik terpilih: {cknowledgesubtopic}")
                    st.session_state.cknowledgesubtopic = cknowledgesubtopic
                cknowledgesubtopic = st.session_state.cknowledgesubtopic
                cfield1 = st.text_input(field1_title,value = default_field1_val)
                cfield2 = st.text_input(field2_title,value = default_field2_val)
                cfield3 = st.text_input(field3_title,value = default_field3_val)
                cknowledgetopicinformation = cknowledgetopic
                cknowledgeinformation = (
                f"{field1_title} : {cfield1}\n"
                f"{field2_title} : {cfield2}\n"
                f"{field3_title} : {cfield3}"
                )
            elif getemplatetopic == "Product Knowledge":
                print("Product knowledge")
                sessiongetfieldtitle = st.session_state.get("selected_field","")
                field1_title,field2_title,field3_title,field4_title,field5_title,field6_title,field7_title,field8_title,field9_title = "","","","","","","","",""
                cfield1,cfield2,cfield3,cfield4,cfield5,cfield6,cfield7,cfield8,cfield9 = "","","","","","","","",""
                if sessiongetstatus == "addnewknowledge":
                    getfieldtemplate = gettemplatefield(cknowledgetopic)
                    print("getfieldtemplate",getfieldtemplate)
                    fields = []
                    # fields = re.findall(r'"(.*?)"', getfieldtemplate)
                    match = re.search(r'^\{(.*)\}$', getfieldtemplate)
                    if match:
                        inner = match.group(1)
                        # Ambil string yang dikutip atau token alfanumerik
                        items = re.findall(r'"(.*?)"|(\w+)', inner)
                        fields = [a or b for a, b in items]

                    print("fields",fields)
                    field1_title = fields[0]
                    field2_title = fields[1]
                    field3_title = fields[2]
                    field4_title = fields[3]
                    field5_title = fields[4]
                    field6_title = fields[5]
                    field7_title = fields[6]
                    field8_title = fields[7]
                    field9_title = fields[8]
                elif sessiongetstatus == "editproduct":
                    field1_title = sessiongetfieldtitle['field1_title']
                    field2_title = sessiongetfieldtitle['field2_title']
                    field3_title = sessiongetfieldtitle['field3_title']
                    field4_title = sessiongetfieldtitle['field4_title']
                    field5_title = sessiongetfieldtitle['field5_title']
                    field6_title = sessiongetfieldtitle['field6_title']
                    field7_title = sessiongetfieldtitle["field7_title"]
                    field8_title = sessiongetfieldtitle['field8_title']
                    field9_title = sessiongetfieldtitle['field9_title']
                default_topicinformation = sessiongetedititem['topic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_subtopic = sessiongetedititem['subtopic'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field1_val = sessiongetedititem['field1_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field2_val = sessiongetedititem['field2_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field3_val = sessiongetedititem['field3_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field4_val = sessiongetedititem['field4_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field5_val = sessiongetedititem['field5_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field6_val = sessiongetedititem['field3_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field7_val = sessiongetedititem['field3_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field8_val = sessiongetedititem['field8_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
                default_field9_val = sessiongetedititem['field3_val'] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

                subtopics = getsubtopic()  # Ambil dari fungsi yang sudah dibuat
                print("subtopics", subtopics)
                # Tambahkan opsi untuk buat baru
                subtopics_with_new = subtopics + ["➕ Buat Sub Topik Baru"]
                if default_subtopic  in subtopics_with_new:
                    default_index = subtopics_with_new.index(default_subtopic)
                else:   
                    default_index = 0

                # Dropdown pilih subtopik
                cknowledgesubtopic = st.selectbox(
                    "Pilih jenis subtopik dari informasi umum:",
                    subtopics_with_new,
                    index = default_index,
                )
                # Jika pilih opsi buat baru
                if cknowledgesubtopic == "➕ Buat Sub Topik Baru":
                    new_subtopic = st.text_input("Masukkan sub topik baru:")
                    if new_subtopic.strip() == "":
                        st.warning("Sub topik tidak boleh kosong.")
                    else:
                        # Tambahkan ke list (atau simpan ke DB)
                        subtopics.append(new_subtopic.strip())
                        st.success(f"Sub topik '{new_subtopic.strip()}' berhasil ditambahkan!")
                        st.session_state.cknowledgesubtopic = new_subtopic.strip()
                        # Bisa juga: st.experimental_rerun() untuk refresh dan masukkan subtopik baru ke dropdown
                else:
                    st.write(f"Sub topik terpilih: {cknowledgesubtopic}")
                    st.session_state.cknowledgesubtopic = cknowledgesubtopic
                cknowledgesubtopic = st.session_state.cknowledgesubtopic
                if "product_section" not in st.session_state:
                    st.session_state.product_section = 1
            # SECTION 1: Form awal
                if st.session_state.product_section == 1:
                    st.subheader("📝 Informasi Produk - Bagian 1")
                    # cnama = st.text_input("Masukan nama pakan produk",value = getnamaproduct)

                    col1, col2 = st.columns(2)
                    with col1:
                        cfield1 = st.text_input(field1_title,value = default_field1_val)
                        cfield2 = st.text_input(field2_title,value = default_field2_val)
                        cfield3 = st.text_input(field3_title,value = default_field3_val)

                    with col2:
                        cfield4 = st.text_input(field4_title,value = default_field4_val)
                        cfield5 = st.text_input(field5_title,value = default_field5_val)
                        cfield6 = st.text_input(field6_title,value = default_field6_val)

                    if st.button("Next ➡️", use_container_width=True):
                        # Simpan input sementara ke session_state
                        st.session_state.cfield1 = cfield1
                        st.session_state.cfield2 = cfield2
                        st.session_state.cfield3 = cfield3
                        st.session_state.cfield4 = cfield4
                        st.session_state.cfield5 = cfield5
                        st.session_state.cfield6 = cfield6
                        st.session_state.product_section = 2
                        st.rerun()
                elif st.session_state.product_section == 2:
                    cfield7 = st.text_area(field7_title, value = default_field7_val)
                    cfield8 = st.text_area(field8_title, value = default_field8_val)
                    cfield9 = st.text_area(field9_title, value = default_field9_val)
                cknowledgetopicinformation = cknowledgetopic
                
                cknowledgeinformation = (
                    f"{field1_title} : {st.session_state.cfield1}\n"
                    f"{field2_title} : {st.session_state.cfield2}\n"
                    f"{field3_title} : {st.session_state.cfield3}\n"
                    f"{field4_title} : {st.session_state.cfield4}\n"
                    f"{field5_title} : {st.session_state.cfield5}\n"
                    f"{field6_title} : {st.session_state.cfield6}\n"
                    f"{field7_title} : {cfield7}\n"
                    f"{field8_title} : {cfield8}\n"
                    f"{field9_title} : {cfield9}\n"
                )

        st.markdown("<br>", unsafe_allow_html=True)

        show_buttons = True
        if cknowledgetopic == "Product Knowledge":
            if st.session_state.get("product_section", 1) == 1:
                show_buttons = False
        if show_buttons:
            col1, col2 = st.columns(2)
            with col1:
                if sessiongetstatus == "editproduct":
                    key = "edit_product"
                    title = "Edit"
                if sessiongetstatus == "addnewknowledge":
                    key = "add_product"
                    title = "Save"

                save_clicked = st.button(title, key=key, use_container_width=True)
                if save_clicked:
                    st.session_state["save_trigger"] = True


            with col2:
                cancel_clicked = st.button("❌ Cancel", key="cancel_button", use_container_width=True)
                if cancel_clicked:
                    st.session_state["cancel_trigger"] = True

        # Trigger logic
        if st.session_state.get("save_trigger", False):
            # st.write("Knowledge Information:", cknowledgeinformation)
            # st.write("cknowledgetopic",cknowledgetopic)
            # st.write("cknowledgesubtopic",cknowledgesubtopic)
            print("cknowledgeinformation",cknowledgeinformation)
            save_data(cknowledgetopic,cknowledgeinformation,cknowledgetopicinformation,cknowledgesubtopic,sessiongetstatus)
            st.session_state.product_section = 1
            st.session_state["save_trigger"] = False  # Reset
            st.session_state.status = "listknowledgeinformation"
            st.rerun()

        if st.session_state.get("cancel_trigger", False):
            st.session_state["cancel_trigger"] = False  # Reset
            st.session_state.status = "listknowledgeinformation"
            st.rerun()

if __name__ == "__main__":
    main()
