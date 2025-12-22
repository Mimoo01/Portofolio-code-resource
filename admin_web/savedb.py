# listknowledgenew.py
from sentence_transformers import SentenceTransformer
from db_connection import get_connection
from transformers import AutoTokenizer
from nltk import sent_tokenize
import re
import streamlit as st

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
                query = """
                    INSERT INTO mtknowledgebase 
                    (cknowledgetopic,cknowledgetopicinformation,cknowledgesubtopic,cknowledgeinformation,cknowledgembedding) 
                    VALUES (%s, %s, %s, %s, %s)
                """
                curr.execute(query, (cknowledgetopic,cknowledgetopicinformation,cknowledgesubtopic, cknowledgeinformation, embeddings))

            elif sessiongetstatus == "editproduct":
                cid = st.session_state.get("selected_data")["id"][0]
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