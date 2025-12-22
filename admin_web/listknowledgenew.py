from calendar import c
from pickletools import stackslice
import streamlit as st
import pandas as pd

from testaddproduct import main as testaddproductpage
from streamlit_modal import Modal
import re
import  psycopg2



def shorten_text(text, max_words=10, threshold=30):
    words = text.split()
    if len(words) > threshold:
        return ' '.join(words[:max_words]) + " ..."
    return text



def build_section_pattern(current_label,section_labels):
    other_labels = [label for label in section_labels if label != current_label]
    return "|".join([re.escape(label) for label in other_labels])

def extract_product_knowledge_info(label, nama_produk_val,info_full,section_labels):
    pattern = build_section_pattern(label,section_labels)
    regex = re.search(
        rf"{label} {re.escape(nama_produk_val)}\s*:\s*(.+?)(?=\n(?:{pattern})|$)",
        info_full,
        re.IGNORECASE | re.DOTALL
    )
    return regex.group(1).strip() if regex else ""



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
    
def getcategory_options():
    query = "SELECT DISTINCT cknowledgetopic FROM mtknowledgebase"
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
    with conn.cursor() as curr:
        curr.execute(query)
        rows = curr.fetchall()
    conn.close()
    return [row[0] for row in rows]  # Ubah list of tuple ke list of string
def fetch_data(filter_option=None):
    query = """
        SELECT cid, cknowledgetopic, cknowledgeinformation, cknowledgetopicinformation, cknowledgesubtopic
        FROM mtknowledgebase
    """
    params = ()
    # conn = psycopg2.connect(
    #     host="43.218.94.232",
    #     port=5432,
    #     database="postgres",
    #     user="postgres",
    #     password="root"
    # )
    conn = psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
    )

    if filter_option:
        query += " WHERE cknowledgetopic = %s"
        params = (filter_option,)

    query += " ORDER BY cid"

    with conn.cursor() as curr:
        curr.execute(query, params)
        rows = curr.fetchall()
        print('rows',rows)

    df = pd.DataFrame(rows, columns=[
        "ID", "type Knowledge", "Knowledge Information", "Topic Knowledge", "Sub Topic Knowledge"
    ])
    print("df",df)

    if filter_option == "Agent Knowledge":
        # Tidak di-groupby, langsung beri New ID urut
        df.insert(0, "New ID", range(1, len(df) + 1))
        return df
    elif filter_option == "Product Knowledge" or filter_option == "FAQ":
        print("filter_option",filter_option)
        # Proses group seperti biasa
        df_grouped = df.groupby(
            ["type Knowledge", "Topic Knowledge", "Sub Topic Knowledge"], as_index=False
        ).agg({
            "Knowledge Information": lambda x: "\n\n".join(x),
            "ID": lambda x: list(x)
        })
        df_grouped.insert(0, "New ID", range(1, len(df_grouped) + 1))
        print("df_grouped",df_grouped)
        return df_grouped
    else:
        print("masuk sini")
        df_grouped = df[["type Knowledge", "Topic Knowledge", "Sub Topic Knowledge", "Knowledge Information", "ID"]].copy()
        df_grouped.insert(0, "New ID", range(1, len(df_grouped) + 1))
        print("df_grouped new",df_grouped)
        return df_grouped

    # else:
    #     # Tidak di-groupby, tapi format data tetap konsisten
    #     df_copy = df.copy()
    #     df_copy["Knowledge Information"] = df_copy["Knowledge Information"].astype(str)
    #     df_copy["ID"] = df_copy["ID"].apply(lambda x: [x])  # ubah jadi list seperti hasil groupby
    #     df_copy.insert(0, "New ID", range(1, len(df_copy) + 1))
    #     return df_copy
    # else:
    #     print("Masuk topic lain")
        

# def fetch_data(filter_option=None):
#     query = "SELECT cid, cknowledgetopic, cknowledgeinformation, cknowledgetopicinformation,cknowledgesubtopic FROM mtknowledgebase"
#     params = ()
#     conn = psycopg2.connect(
#             host="43.218.94.232",
#             port=5432,
#             database="postgres",
#             user="postgres",
#             password="root"
#         )

#     if filter_option:
#         query += " WHERE cknowledgetopic = %s"
#         params = (filter_option,)

#     query += " ORDER BY cid"

#     with conn.cursor() as curr:
#         curr.execute(query, params)
#         rows = curr.fetchall()

#     df = pd.DataFrame(rows, columns=["ID", "type Knowledge", "Knowledge Information", "Topic Knowledge","Sub Topic Knowledge"])

#     df_grouped = df.groupby(["type Knowledge", "Topic Knowledge","Sub Topic Knowledge"], as_index=False).agg({
#         "Knowledge Information": lambda x: "\n\n".join(x),
#         "ID": lambda x: list(x)
#     })

#     df_grouped.insert(0, "New ID", range(1, len(df_grouped) + 1))

#     return df_grouped


import psycopg2

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


def delete_knowledge(id):
    print("deleting knowledge with id",id[0])

    with psycopg2.connect(
        dbname="skripsi",
        user="postgres",
        password="root",
        host="localhost"
        # host="43.218.94.232",
        # port=5432,
        # database="postgres",
        # user="postgres",
        # password="root"
    ) as conn:
        with conn.cursor() as curr:
            curr.execute("DELETE FROM mtknowledgebase WHERE cid = %s", (id[0],))

import re

# def extract_custom_fields(knowledge_info):
#     # Tangkap pasangan key : value (hingga titik akhir kalimat)
#     matches = re.findall(r"(.*?):\s*(.*?\.)", knowledge_info)

#     # Ubah ke dalam list of dict
#     result = [{"key": key.strip(), "value": value.strip()} for key, value in matches]

#     return result

def extract_custom_fields(knowledge_info):
    # Tangkap pasangan key: value sampai akhir baris
    matches = re.findall(r"^(.*?):\s*(.*)$", knowledge_info, flags=re.MULTILINE)

    result = [{"key": key.strip(), "value": value.strip()} for key, value in matches]
    return result


def listknowledge_page():
    if "status" not in st.session_state:
        st.session_state.status = "listknowledgeinformation"

    if st.session_state.status == "listknowledgeinformation":
        st.title("List Product Information")
        categories = getcategory_options()

        filter_option = st.selectbox(
            "Pilih kategori:",
            categories
            # ("FAQ", "Product Knowledge", "Agent Knowledge","Lain lain")
        )

        getemplatetopic = ""

        # Tentukan placeholder berdasarkan kategori
        if filter_option == "FAQ":
            search_placeholder = "🔍 Cari pertanyaan..."
        elif filter_option == "Product Knowledge":
            search_placeholder = "🔍 Cari nama produk"
        elif filter_option == "Agent Knowledge":
            search_placeholder = "🔍 Cari nama agent, lokasi, atau sub-agent..."
        else:
            search_placeholder = "🔍 Cari data..."

        # Tampilkan input pencarian dengan placeholder
        search_query = st.text_input(
            label="Cari data:",
            placeholder=search_placeholder
        )


        if st.button("➕ Add New Information Knowledge", use_container_width=True):
            st.session_state.status = "addnewknowledge"

        df = fetch_data(filter_option)
        print("result df",df)

        if search_query:
            if filter_option == "FAQ":
                df = df[df["Topic Knowledge"].str.contains(search_query, case=False, na=False) |
                        df["Knowledge Information"].str.contains(search_query, case=False, na=False) |
                        df["Sub Topic Knowledge"].str.contains(search_query, case=False, na=False)] 

            elif filter_option == "Product Knowledge":
                df = df[df["Knowledge Information"].str.contains(search_query, case=False, na=False)]
            elif filter_option == "Agent Knowledge":
                df = df[df["Knowledge Information"].str.contains(search_query, case=False, na=False)]

        if df.empty:
            st.info("Belum ada data knowledge yang disimpan.")
            return
        if filter_option not in ["FAQ", "Product Knowledge", "Agent Knowledge"]:
            result = []
            getemplatetopic = gettemplatetopic(filter_option)
            print("get template topic",getemplatetopic)
            if getemplatetopic== "FAQ":
                col1, col2, col3, col4, col5, col6,col7 = st.columns([1,1,1, 1, 1, 1,1])
            # extract_result = extract_custom_fields(df["Knowledge Information"])
                col1.markdown("**ID**")
                col2.markdown("**Topik**")
                col3.markdown("**Sub topik**")
                for i in range(len(df)):
                    info_raw = str(df.iloc[i]["Knowledge Information"])
                    print("info_raw",info_raw)
                    result = extract_custom_fields(info_raw)
                print("resul raw",result)

                    # col5.markdown(f"**{result[n]['key']}**")
                col4.markdown(f"**{result[0]['key']}**")
                col5.markdown(f"**{result[1]['key']}**")
                col6.markdown("**Edit**")
                col7.markdown("**Delete**")
            elif getemplatetopic == "Agent Knowledge":
                col1, col2, col3, col4, col5, col6,col7,col8 = st.columns([1,1,1, 1, 1, 1,1,1])
                col1.markdown("**ID**")
                col2.markdown("**Topik**")
                col3.markdown("**Sub topik**")
                for i in range(len(df)):
                    info_raw = str(df.iloc[i]["Knowledge Information"])
                    result = extract_custom_fields(info_raw)

                    # col5.markdown(f"**{result[n]['key']}**")
                col4.markdown(f"**{result[0]['key']}**")
                col5.markdown(f"**{result[1]['key']}**")
                col6.markdown(f"**{result[2]['key']}**")
                col7.markdown("**Edit**")
                col8.markdown("**Delete**")
                
        if filter_option == "FAQ":
            # col1, col2, col3, col4, col5, col6,col7 = st.columns([1,1,2, 3, 1, 1,1])
            col1, col2, col3, col4, col5, col6,col7 = st.columns([1,1,1, 2, 2, 1,1])
            col1.markdown("**ID**")
            col2.markdown("**Topik**")
            col3.markdown("**Sub topik**")
            col4.markdown("**Contoh Pertanyaan**")
            col5.markdown("**Informasi**")
            col6.markdown("**Edit**")
            col7.markdown("**Delete**")

        elif filter_option == "Agent Knowledge":
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 2, 2, 2, 1, 1, 0.5])
            col1.markdown("**ID**")
            col2.markdown("**Knowledge Type**")
            col3.markdown("**Nama Agent**")
            col4.markdown("**Lokasi**")
            col5.markdown("**Sub Agent**")
            col6.markdown("**Edit**")
            col7.markdown("**Delete**")
            col8.markdown("")

        for i in range(len(df)):
            if filter_option == "Agent Knowledge":
                col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([0.5, 1.5, 2, 2, 2, 1, 1, 0.5])
                print("df Agent Knowledge",df)
                col1.write(df.iloc[i]["New ID"])
                col2.write(df.iloc[i]["type Knowledge"])
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
                        "subtopic":df.iloc[i]["Topic Knowledge"],
                        "nama agent": nama_agent,
                        "lokasi": lokasi,
                        "sub agent": sub_agent
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
            elif filter_option == "Product Knowledge":
                produk_id = df.iloc[i]["New ID"]
                topik = df.iloc[i]["Topic Knowledge"]
                info_full = df.iloc[i]["Knowledge Information"]
                print("info full",info_full)

                section_labels = [
                "Nama produk",
                "Katalog produk",
                "Jenis produk",
                "Nama brand produk",
                "Fungsi / tujuan produk",
                "Kelemahan kelebihan produk",
                "Kandungan yang terdapat didalam produk",
                "Informasi lain produk",
                "Jenis / bentuk Pakan ternak",
                "Jenis produk lain"
                ]

                nama_produk = re.search(r"Nama produk\s*:\s*([^.]+)",info_full, re.IGNORECASE)
                nama_produk_val = nama_produk.group(1).strip() if nama_produk else ""

                # Ekstrak semua bagian
                deskripsi_val = extract_product_knowledge_info("Katalog produk", nama_produk_val,info_full,section_labels)
                jenis_val = extract_product_knowledge_info("Jenis produk", nama_produk_val,info_full,section_labels)
                brand_val = extract_product_knowledge_info("Nama brand produk", nama_produk_val,info_full,section_labels)
                fungsi_val = extract_product_knowledge_info("Fungsi / tujuan produk", nama_produk_val,info_full,section_labels)
                kelebihan_val = extract_product_knowledge_info("Kelemahan kelebihan produk", nama_produk_val,info_full,section_labels)
                kandungan_val = extract_product_knowledge_info("Kandungan yang terdapat didalam produk", nama_produk_val,info_full,section_labels)
                info_lain_val = extract_product_knowledge_info("Informasi lain produk", nama_produk_val,info_full,section_labels)





                ketjenisproduk = ""

                if jenis_val == "Pakan Ternak":
                    ketjenisproduk = re.search(r"Jenis / bentuk Pakan ternak\s*:\s*(.+?)(?:\.\s*|$)", info_full, re.IGNORECASE)
                elif jenis_val == "Produk lain":
                    ketjenisproduk = re.search(r"Jenis produk lain\s*:\s*(.+?)(?:\.\s*|$)", info_full, re.IGNORECASE)



                ketjenisproduk_val = ketjenisproduk.group(1).strip() if ketjenisproduk else ""
                print("tesssss jenis val",jenis_val)

                # Tampilkan di UI
                with st.expander(f"🧾 {produk_id}. {topik}"):
                    st.markdown(f"**Nama Produk :** {nama_produk_val}")
                    st.markdown(f"**Katalog Produk :** {deskripsi_val}")
                    st.markdown(f"**Jenis Produk :** {jenis_val}")
                    if jenis_val == "Pakan Ternak":
                        st.markdown(f"**Jenis Pakan Ternak :** {ketjenisproduk_val}")
                    elif jenis_val == "Produk lain":
                        st.markdown(f"**Jenis Produk Lain :** {ketjenisproduk_val}")
                    st.markdown(f"**Brand Produk :** {brand_val}")
                    st.markdown(f"**Kegunaan Produk :**\n\n {fungsi_val}")
                    st.markdown(f"**Kelemahan / Kelebihan Produk :**\n\n {kelebihan_val}")
                    st.markdown(f"**Kandungan Produk :**\n\n {kandungan_val}")
                    st.markdown(f"**Informasi Lain Produk :**\n\n {info_lain_val}")

                    col_edit, col_delete = st.columns([1, 1])
                    if col_edit.button("✏️ Edit", key=f"edit_{i}"):
                        st.session_state.status = "editproduct"
                        st.session_state.selected_data = {
                            "id": df.iloc[i]["ID"],
                            "type": df.iloc[i]["type Knowledge"],
                            "topic": df.iloc[i]["Topic Knowledge"],
                            "subtopic": jenis_val,
                            # "information": df.iloc[i]["Knowledge Information"]
                            "nama produk":nama_produk_val,
                            "Katalog produk":deskripsi_val,
                            "Jenis produk":jenis_val,
                            "Brand produk": brand_val,
                            "Fungsi produk":fungsi_val,
                            "Kelemahan kelebihan produk":kelebihan_val,
                            "Kandungan produk":kandungan_val,
                            "info lain":info_lain_val

                        }

                    modal = Modal("Apa anda yakin ?", key=f"modal_{i}", padding=20)
                    if col_delete.button("🗑️ Hapus", key=f"delete_{i}"):
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
            elif filter_option not in ["Product Knowledge","Agent Knowledge","FAQ"]:
                print("test",len(df))  # Budidaya Ternak
                if getemplatetopic == "FAQ":
                    col1, col2, col3, col4, col5, col6, col7 = st.columns([1,1,1,1,1,1,1])
                    col1.write(df.iloc[i]["New ID"])
                    col2.write(df.iloc[i]["type Knowledge"])
                    col3.write(df.iloc[i]["Sub Topic Knowledge"])
                    # col4.write(df.iloc[i]["Topic Knowledge"])
                    extractresult = extract_custom_fields(df.iloc[i]["Knowledge Information"])
                    print("extract result",extractresult)
                    col4.write(extractresult[0]['value'])
                    col5.write(extractresult[1]['value'])
                    if col6.button("Edit",key = f"edit{i}"):
                        print("edit")
                        st.session_state.status = "editproduct"
                        st.session_state.selected_field = {
                            "field1_title":extractresult[0]['key'],
                            "field2_title":extractresult[1]['key']
                        }
                        
                        st.session_state.selected_data ={
                            "id": df.iloc[i]["ID"],
                            "type": df.iloc[i]["type Knowledge"],
                            "topic": df.iloc[i]["Topic Knowledge"],
                            "subtopic":df.iloc[i]["Sub Topic Knowledge"],
                            "field1_val":extractresult[0]['value'],
                            "field2_val":extractresult[1]['value']
                        }
                    if col7.button("delete",key=f"delete{i}"):
                        print("delete")
                elif getemplatetopic == "Agent Knowledge":
                    col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
                    col1.write(df.iloc[i]["New ID"])
                    col2.write(df.iloc[i]["type Knowledge"])
                    col3.write(df.iloc[i]["Sub Topic Knowledge"])
                    extractresult = extract_custom_fields(df.iloc[i]["Knowledge Information"])
                    print("extract result agent knowledge",extractresult)
                    col4.write(extractresult[0]['value'])
                    col5.write(extractresult[1]['value'])
                    col6.write(extractresult[2]['value'])
                    if col7.button("edit",key = f"edit{i}"):
                        print("edit")
                        st.session_state.status = "editproduct"
                        st.session_state.selected_field = {
                            "field1_title":extractresult[0]['key'],
                            "field2_title":extractresult[1]['key'],
                            "field3_title":extractresult[2]['key']
                        }
                        st.session_state.selected_data ={
                            "id": df.iloc[i]["ID"],
                            "type": df.iloc[i]["type Knowledge"],
                            "topic": df.iloc[i]["Topic Knowledge"],
                            "subtopic":df.iloc[i]["Sub Topic Knowledge"],
                            "field1_val":extractresult[0]['value'],
                            "field2_val":extractresult[1]['value'],
                            "field3_val":extractresult[2]['value']
                        }

                    if col8.button("delete",key = f"delete{i}"):
                        print("delete")
                elif getemplatetopic == "Product Knowledge":
                    extractresult = extract_custom_fields(df.iloc[i]["Knowledge Information"])
                    print("extract result product knowledge",extractresult)
                    with st.expander(f"{filter_option}"):
                        st.markdown(f"**{extractresult[0]['key']}** : {extractresult[0]['value']}")
                        st.markdown(f"**{extractresult[1]['key']}** : {extractresult[1]['value']}")
                        st.markdown(f"**{extractresult[2]['key']}** : {extractresult[2]['value']}")
                        st.markdown(f"**{extractresult[3]['key']}** : {extractresult[3]['value']}")
                        st.markdown(f"**{extractresult[4]['key']}** : {extractresult[4]['value']}")
                        st.markdown(f"**{extractresult[5]['key']}** : {extractresult[5]['value']}")
                        st.markdown(f"**{extractresult[6]['key']}** : {extractresult[6]['value']}")
                        st.markdown(f"**{extractresult[7]['key']}** : {extractresult[7]['value']}")
                        # st.markdown(f"**{extractresult[8]['key']}** : {extractresult[8]['value']}")
                        col_edit, col_delete = st.columns([1, 1])
                        if col_edit.button("edit",key = f"edit{i}"):
                            st.session_state.status = "editproduct"
                            print("edit")
                            st.session_state.selected_data = {
                                "id": df.iloc[i]["ID"],
                                "type": df.iloc[i]["type Knowledge"],
                                "topic": df.iloc[i]["Topic Knowledge"],
                                "subtopic":df.iloc[i]["Sub Topic Knowledge"],
                                "field1_val":extractresult[0]['value'],
                                "field2_val":extractresult[1]['value'],
                                "field3_val":extractresult[2]['value'],
                                "field4_val":extractresult[3]['value'],
                                "field5_val":extractresult[4]['value'],
                                "field6_val":extractresult[5]['value'],
                                "field7_val":extractresult[6]['value'],
                                "field8_val":extractresult[7]['value'],
                                "field9_val":extractresult[8]['value']
                            }

                            st.session_state.selected_field = {
                                "field1_title":extractresult[0]['key'],
                                "field2_title":extractresult[1]['key'],
                                "field3_title":extractresult[2]['key'],
                                "field4_title":extractresult[3]['key'],
                                "field5_title":extractresult[4]['key'],
                                "field6_title":extractresult[5]['key'],
                                "field7_title":extractresult[6]['key'],
                                "field8_title":extractresult[7]['key'],
                                "field9_title":extractresult[8]['key'],
                            }


                        if col_delete.button("delete",key = f"delete{i}"):
                            print("delete")

                


            elif filter_option == "FAQ":  # FAQ
                # col1, col2, col3, col4, col5, col6 ,col7= st.columns([1, 2, 2, 3, 1, 1,1])
                col1, col2, col3, col4, col5, col6,col7 = st.columns([1,1,1, 2, 2, 1,1])
                print("df",df)
                col1.write(df.iloc[i]["New ID"])
                col2.write(df.iloc[i]["type Knowledge"])
                col3.write(df.iloc[i]["Sub Topic Knowledge"])
                col4.write(df.iloc[i]["Topic Knowledge"])
                # col5.write(shorten_text(df.iloc[i]["Knowledge Information"]))
                info_raw = str(df.iloc[i]["Knowledge Information"])
                match = re.search(r'informasi\s*:\s*(.*)', info_raw, re.IGNORECASE | re.DOTALL)

                if match:
                    info_cleaned = match.group(1).strip()
                else:
                    info_cleaned = info_raw.strip()
                col5.write(shorten_text(info_cleaned))

                if col6.button("✏️", key=f"edit_{i}"):
                    st.session_state.status = "editproduct"
                    st.session_state.selected_data = {
                        "id": df.iloc[i]["ID"],
                        "type": df.iloc[i]["type Knowledge"],
                        "topic": df.iloc[i]["Topic Knowledge"],
                        "subtopic":df.iloc[i]["Sub Topic Knowledge"],
                        "information": info_cleaned
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

    elif st.session_state.status == "addnewknowledge":
        if st.button("⬅️ Back to Product List", use_container_width=True):
            st.session_state.status = "listknowledgeinformation"
            st.rerun()
        testaddproductpage()

    elif st.session_state.status == "editproduct":
        if st.button("⬅️ Back to Product List", use_container_width=True):
            st.session_state.status = "listknowledgeinformation"
            st.rerun()
        # addproductpage()
        testaddproductpage()


