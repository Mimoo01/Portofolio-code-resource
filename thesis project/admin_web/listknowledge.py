import streamlit as st
import pandas as pd

from db_connection import get_connection
from add_product import main as addproductpage
from testaddproduct import main as testaddproductpage
from streamlit_modal import Modal
from list_question import listqa_page as list_question_page
import re

conn = get_connection()
curr = conn.cursor()

def shorten_text(text, max_words=10, threshold=30):
    words = text.split()
    if len(words) > threshold:
        return ' '.join(words[:max_words]) + " ..."
    return text

# def fetch_data():
#     curr.execute("SELECT cid, cknowledgetype, cknowledgeinformation, cknowledgetopic FROM mtknowledgebase ORDER BY cid")
#     rows = curr.fetchall()
#     df = pd.DataFrame(rows, columns=["ID", "type Knowledge", "Knowledge Information", "Topic Knowledge"])

#     # Gabungkan berdasarkan Type dan Topic
#     df_grouped = df.groupby(["type Knowledge", "Topic Knowledge"], as_index=False).agg({
#         "Knowledge Information": lambda x: "\n\n".join(x),
#         "ID": lambda x: list(x)
#     })

#     # Reset ID: tambahkan kolom ID baru dari 1 hingga n
#     df_grouped.insert(0, "New ID", range(1, len(df_grouped) + 1))

#     return df_grouped

def extract_agent_info(text):
    """
    Ekstrak nama agent, lokasi, dan sub-agent dari teks Knowledge Information.
    """
    if not text:
        return None, None, None

    nama_agent = None
    lokasi = None
    sub_agent = None

    try:
        nama_agent_match = re.search(r"nama agent\s*:\s*(.+)", text, re.IGNORECASE)
        lokasi_match = re.search(r"lokasi\s*:\s*(.+)", text, re.IGNORECASE)
        sub_agent_match = re.search(r"sub agent\s*:\s*(.+)", text, re.IGNORECASE)

        if nama_agent_match:
            nama_agent = nama_agent_match.group(1).strip()

        if lokasi_match:
            lokasi = lokasi_match.group(1).strip()

        if sub_agent_match:
            sub_agent = sub_agent_match.group(1).strip()

    except Exception as e:
        print(f"Error extracting agent info: {e}")

    return nama_agent, lokasi, sub_agent
    

def fetch_data(filter_option=None):
    query = "SELECT cid, cknowledgetype, cknowledgeinformation, cknowledgetopic FROM mtknowledgebase"
    params = ()

    if filter_option:
        query += " WHERE cknowledgetype = %s"
        params = (filter_option,)

    query += " ORDER BY cid"
    curr.execute(query, params)
    rows = curr.fetchall()
    df = pd.DataFrame(rows, columns=["ID", "type Knowledge", "Knowledge Information", "Topic Knowledge"])

    # Gabungkan berdasarkan Type dan Topic
    df_grouped = df.groupby(["type Knowledge", "Topic Knowledge"], as_index=False).agg({
        "Knowledge Information": lambda x: "\n\n".join(x),
        "ID": lambda x: list(x)
    })

    # Hilangkan prefix "deskripsi produk dari {topic}:" untuk Product Knowledge
    for idx, row in df_grouped.iterrows():
        if row["type Knowledge"] == "Product Knowledge":
            prefix = f"deskripsi produk dari {row['Topic Knowledge']}: "
            if row["Knowledge Information"].startswith(prefix):
                df_grouped.at[idx, "Knowledge Information"] = row["Knowledge Information"].replace(prefix, "", 1)
        elif row["type Knowledge"] == "Agent Knowledge":
            text = row["Knowledge Information"]
            nama_agent = re.search(r"nama agent\s*:\s*(.+)", text, re.IGNORECASE)
            lokasi = re.search(r"lokasi\s*:\s*(.+)", text, re.IGNORECASE)
            sub_agent = re.search(r"sub agent\s*:\s*(.+)", text, re.IGNORECASE)
            nama_agent_value = nama_agent.group(1).strip() if nama_agent else None
            lokasi_value = lokasi.group(1).strip() if lokasi else None
            sub_agent_value = sub_agent.group(1).strip() if sub_agent else None
            print("nama agent",nama_agent_value)
            print("lokasi agent",lokasi_value)
            print("sub agent : ",sub_agent_value)
            # fetchh ke tabel
            df_grouped.at[idx, "Nama Agent"] = nama_agent_value
            df_grouped.at[idx, "Lokasi"] = lokasi_value
            df_grouped.at[idx, "Sub Agent"] = sub_agent_value



    # Reset ID: tambahkan kolom ID baru dari 1 hingga n
    df_grouped.insert(0, "New ID", range(1, len(df_grouped) + 1))

    return df_grouped



def delete_knowledge(id):
    curr.execute("DELETE FROM mtknowledgebase WHERE cid = %s", (id,))
    conn.commit()

def listknowledge_page():
    if "status" not in st.session_state:
        st.session_state.status = "listknowledgeinformation"

    if st.session_state.status == "listknowledgeinformation":

        st.title("List Productsss Information")
        filter_option = st.selectbox(
            "Pilih kategori:",
            ("FAQ", "Product Knowledge", "Agent Knowledge")
        )

        if st.button("➕ Add New Information Knowledge", use_container_width=True):
            st.session_state.status = "addnewknowledge"

        df = fetch_data(filter_option)

        if df.empty:
            st.info("Belum ada data knowledge yang disimpan.")
            return

        # --- Set Header Kolom
        if filter_option == "FAQ":
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 3, 1, 1])
            col1.markdown("**ID**")
            col2.markdown("**Knowledge Type**")
            col3.markdown("**Pertanyaan**")
            col4.markdown("**Jawaban**")
            col5.markdown("**Edit**")
            col6.markdown("**Delete**")
        elif filter_option == "Product Knowledge":
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 3, 1, 1])
            col1.markdown("**ID**")
            col2.markdown("**Knowledge Type**")
            col3.markdown("**Nama Produk**")
            col4.markdown("**Informasi Produk**")
            col5.markdown("**Edit**")
            col6.markdown("**Delete**")
        elif filter_option == "Agent Knowledge":
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 2, 2, 2, 1, 1, 0.5])
            col1.markdown("**ID**")
            col2.markdown("**Knowledge Type**")
            col3.markdown("**Nama Agent**")
            col4.markdown("**Lokasi**")
            col5.markdown("**Sub Agent**")
            col6.markdown("**Edit**")
            col7.markdown("**Delete**")
            col8.markdown("")  # spacing

        # --- Loop data per baris
        for i in range(len(df)):
            if filter_option == "Agent Knowledge":
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 2, 2, 2, 1, 1, 0.5])
                col1.write(df.iloc[i]["New ID"])
                col2.write(df.iloc[i]["type Knowledge"])

                # Extract agent info
                nama_agent, lokasi, sub_agent = extract_agent_info(df.iloc[i]["Knowledge Information"])
                col3.write(nama_agent or "-")
                col4.write(lokasi or "-")
                col5.write(sub_agent or "-")

                if col6.button("✏️", key=f"edit_{i}"):
                    st.session_state.status = "editproduct"
                    st.session_state.selected_data = {
                        "id": df.iloc[i]["ID"],
                        "type": df.iloc[i]["type Knowledge"],
                        "topic": df.iloc[i]["Topic Knowledge"],
                        "information": df.iloc[i]["Knowledge Information"]
                    }

                modal = Modal("Apa anda yakin ?", key=f"modal_{i}", padding=20)

                if col7.button("🗑️", key=f"delete_{i}"):
                    modal.open()
                if modal.is_open():
                    with modal.container():
                        st.markdown(
                            """
                            <div style='text-align:center'>
                            <h3 style='color:#cc0000;'>⚠️ Konfirmasi Penghapusan</h3>
                            <p style='color:gray; font-size: 14px;'>Tindakan ini akan menghapus produk</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        col_confirm, col_cancel = st.columns(2)

                        with col_confirm:
                            if st.button("Ya", key=f"confirm_delete_{i}", use_container_width=True):
                                delete_knowledge(df.iloc[i]["ID"])
                                modal.close()
                                st.success(f"Data dengan ID {df.iloc[i]['ID']} telah dihapus.")
                                st.experimental_rerun()
                        with col_cancel:
                            if st.button("Tidak", key=f"cancel_delete_{i}", use_container_width=True):
                                modal.close()
                                st.success("Penghapusan dibatalkan.")

            else:
                col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 3, 1, 1])
                col1.write(df.iloc[i]["New ID"])
                col2.write(df.iloc[i]["type Knowledge"])
                col3.write(df.iloc[i]["Topic Knowledge"])
                col4.write(shorten_text(df.iloc[i]["Knowledge Information"]))

                if col5.button("✏️", key=f"edit_{i}"):
                    st.session_state.status = "editproduct"
                    st.session_state.selected_data = {
                        "id": df.iloc[i]["ID"],
                        "type": df.iloc[i]["type Knowledge"],
                        "topic": df.iloc[i]["Topic Knowledge"],
                        "information": df.iloc[i]["Knowledge Information"]
                    }

                modal = Modal("Apa anda yakin ?", key=f"modal_{i}", padding=20)

                if col6.button("🗑️", key=f"delete_{i}"):
                    modal.open()
                if modal.is_open():
                    with modal.container():
                        st.markdown(
                            """
                            <div style='text-align:center'>
                            <h3 style='color:#cc0000;'>⚠️ Konfirmasi Penghapusan</h3>
                            <p style='color:gray; font-size: 14px;'>Tindakan ini akan menghapus produk</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        col_confirm, col_cancel = st.columns(2)

                        with col_confirm:
                            if st.button("Ya", key=f"confirm_delete_{i}", use_container_width=True):
                                delete_knowledge(df.iloc[i]["ID"])
                                modal.close()
                                st.success(f"Data dengan ID {df.iloc[i]['ID']} telah dihapus.")
                                st.experimental_rerun()
                        with col_cancel:
                            if st.button("Tidak", key=f"cancel_delete_{i}", use_container_width=True):
                                modal.close()
                                st.success("Penghapusan dibatalkan.")

    elif st.session_state.status == "addnewknowledge":
        if st.button("⬅️ Back to Product List", use_container_width=True):
            st.session_state.status = "listknowledgeinformation"
            st.rerun()
        # addproductpage()
        testaddproductpage()

    elif st.session_state.status == "editproduct":
        if st.button("⬅️ Back to Product List", use_container_width=True):
            st.session_state.status = "listknowledgeinformation"
            st.rerun()
        addproductpage()







