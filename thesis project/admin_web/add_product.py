import streamlit as st
from db_connection import get_connection
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
import numpy as np


# Koneksi ke database
conn = get_connection()
curr = conn.cursor()

def save_data(cknowledgetype, cknowledgetopic, cknowledgeinformation):
    try:
        tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/LaBSE")
        embedding_model = SentenceTransformer("sentence-transformers/LaBSE")
        token_limit = 500

        # Langkah 1: Split jadi kalimat
        sentences = [s.strip() for s in cknowledgeinformation.strip().split(".") if s]

        # Langkah 2: Chunking
        chunks = []
        chunk = ""
        for sentence in sentences:
            tokens = tokenizer.tokenize(chunk + " " + sentence)
            if len(tokens) <= token_limit:
                chunk += " " + sentence
            else:
                chunks.append(chunk.strip())
                chunk = sentence
        if chunk:
            chunks.append(chunk.strip())

        # Langkah 3: Tambahkan prefix ke chunk kedua dan seterusnya
        prefix = ""
        if cknowledgetype == "Product Knowledge":
            subprefix = f"Nama produk : {cknowledgetopic}\n"
            subprefix2 = f"deskripsi produk {cknowledgetopic}: "
            prefix = subprefix + subprefix2

            

        updated_chunks = []
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                updated_chunks.append(f"{prefix}{chunk}")  # Chunk kedua dst pakai prefix
                # updated_chunks.append(chunk)  # Chunk pertama tanpa prefix
            else:
                updated_chunks.append(f"{prefix}{chunk}")  # Chunk kedua dst pakai prefix

        # Langkah 4: Simpan tiap chunk ke database
        for chunked_info in updated_chunks:
            tokens = tokenizer.tokenize(chunked_info)
            embeddings = embedding_model.encode(chunked_info)
            if isinstance(embeddings, np.ndarray):
                embeddings = embeddings.tolist()
            
            query = """
                INSERT INTO mtknowledgebase 
                (cknowledgetype, cknowledgeinformation, embedding_information, cknowledgetopic) 
                VALUES (%s, %s, %s, %s)
            """
            curr.execute(query, (cknowledgetype, chunked_info, embeddings, cknowledgetopic))
        
        conn.commit()
        st.success(f"{len(updated_chunks)} potongan data berhasil disimpan!")

    except Exception as e:
        conn.rollback()
        st.error(f"Terjadi kesalahan: {e}")




def main():
    sessiongetstatus = st.session_state.get("status")
    st.write("session",sessiongetstatus)
    if sessiongetstatus == "addnewknowledge":
        st.title("Add your new knowledge")
    if sessiongetstatus == "editproduct":
        st.title("Edit your product knowledge")
        sessiongetedititem = st.session_state.get("selected_data")
        st.write("sessiongetedititem",sessiongetedititem)


    
  

    options = ["FAQ", "Product Knowledge","Agent Knowledge"]
    # cknowledgetype = st.selectbox("Pilih topik knowledge yang akan dimasukkan", options)
    default_type = options.index(sessiongetedititem["type"]) if sessiongetstatus == "editproduct" and sessiongetedititem else 0
    cknowledgetype = st.selectbox("Pilih topik knowledge yang akan dimasukkan", options, index=default_type)


    topik_informasi = data_informasi = ""
    name_product = description_product = function_product = plus_minus_product = ""

    if cknowledgetype == "FAQ":
        st.subheader("📝 Informasi Umum")
        default_topic = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
        default_info = sessiongetedititem["information"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

        cknowledgetopic = st.text_input("Masukkan topik seputar pertanyaan umum yang akan dijawab", value=default_topic)
        cknowledgeinformation = st.text_area("Masukkan data dari informasi umum", value=default_info)
        # cknowledgetopic = st.text_input("Masukkan topik seputar pertanyaan umum yang akan dijawab")
        # cknowledgeinformation = st.text_area("Masukkan data dari informasi umum")
       
    elif cknowledgetype == "Product Knowledge":
        st.subheader("📝 Product Knowledge")
        default_topic = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
        default_info = sessiongetedititem["information"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""

        cknowledgetopic = st.text_input("Masukkan Nama Produk", value=default_topic)
        cknowledgeinformation = st.text_area("Masukkan deskripsi produk", value=default_info)
        # cknowledgetopic = st.text_input("Masukkan Nama Produk")
        # cknowledgeinformation = st.text_area("Masukkan deskripsi produk")
    elif cknowledgetype == "Agent Knowledge":
            
            st.subheader("📝 Agent Knowledge")
            default_topic = sessiongetedititem["topic"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
            default_info = sessiongetedititem["information"] if sessiongetstatus == "editproduct" and sessiongetedititem else ""
    
            cknowledgetopic = st.text_input("Masukkan nama agent", value=default_topic)
            cknowledgeareaagent = st.text_area("Masukkan area kawasan agent", value=default_info)
            cknowledgesubagent = st.text_input("Masukkan nama sub agent", value=default_info)
            cknowledgeinformation = (
                f"Anda dapat membeli pakan ternak  melalui agent serta sub agent berikut :\n"
                f"nama agent : {cknowledgetopic}" 
                f"lokasi     : {cknowledgeareaagent}"
                f"sub agent  : {cknowledgesubagent}"
            )
            # cknowledgetopic = st.text_input("Masukkan topik seputar agent knowledge")
            # cknowledgeinformation = st.text_area("Masukkan data dari agent knowledge")


    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol Save dan Cancel dengan layout 2 kolom
    col1, col2 = st.columns(2)

    with col1:
        if sessiongetstatus == "editproduct":
            key = "edit_product"
            title = "Edit"
        if sessiongetstatus == "addnewknowledge":
            key = "add_product"
            title = "Save"

        save_clicked = st.button(title, key=key,use_container_width=True)
        if save_clicked:
            st.session_state["save_trigger"] = True

    with col2:
        cancel_clicked = st.button("❌ Cancel", key="cancel_button",use_container_width=True)
        if cancel_clicked:
            st.session_state["cancel_trigger"] = True

    # Trigger logic
    if st.session_state.get("save_trigger", False):
        st.write("Knowledge Information:", cknowledgeinformation)
        save_data(cknowledgetype,cknowledgetopic, cknowledgeinformation)
        st.session_state["save_trigger"] = False  # Reset

    if st.session_state.get("cancel_trigger", False):
        st.session_state["cancel_trigger"] = False  # Reset
        # st.experimental_rerun()
        st.rerun()

if __name__ == "__main__":
    main()
