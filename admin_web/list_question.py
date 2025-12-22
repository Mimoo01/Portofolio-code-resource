# import streamlit as st
# import pandas as pd
# from db_connection import get_connection

# # Koneksi ke database
# conn = get_connection()
# curr = conn.cursor()

# # Fungsi untuk mengambil data dari database
# def fetch_data():
#     curr.execute("SELECT * FROM mtlogquestionuser")
#     rows = curr.fetchall()
#     return rows

# # Halaman utama list Q&A
# def listqa_page():
#     st.title("List All Questions from User")

#     result = fetch_data()

#     if not result:
#         st.warning("Belum ada pertanyaan yang masuk.")
#         return

#     # Unpacking hasil query
#     ids, member_names, questions, answers, dates, userfeedback, guideknowledge = zip(*result)

#     # Menyusun data ke dalam dictionary
#     data = {
#         "ID": list(ids),
#         "Member Name": list(member_names),
#         "Question": list(questions),
#         "Answer": list(answers),
#         "Date": list(dates),
#         "User Feedback": list(userfeedback),
#         "status": list(guideknowledge)
#     }

#     # Membuat DataFrame
#     df = pd.DataFrame(data)

#     # Styling tabel HTML agar teks panjang ter-wrap dan kolom Answer dilebarkan
#     table_style = """
#         <style>
#             table {
#                 width: 100%;
#                 border-collapse: collapse;
#                 table-layout: fixed;
#                 word-wrap: break-word;
#             }
#             th, td {
#                 border: 1px solid #ddd;
#                 padding: 10px;
#                 white-space: pre-wrap;
#                 word-wrap: break-word;
#                 vertical-align: top;
#                 text-align: center;
#             }
#             th {
#                 background-color: #F06423;
#                 color: white;
#             }
#         </style>
#     """

#     # Ubah HTML dari DataFrame dan inject colgroup untuk mengatur lebar kolom
#     table_html = df.to_html(escape=False, index=False)

#     # Atur lebar kolom menggunakan <colgroup> — sesuaikan persentase sesuai kebutuhan
#     table_html = table_html.replace(
#         '<table border="1" class="dataframe">',
#         '''
#         <table border="1" class="dataframe">
#         <colgroup>
#             <col style="width: 7%;">   <!-- ID -->
#             <col style="width: 20%;">  <!-- Member Name -->
#             <col style="width: 15%;">  <!-- Question -->
#             <col style="width: 35%;">  <!-- Answer -->
#             <col style="width: 15%;">  <!-- Date -->
#             <col style="width: 20%;">  <!-- User Feedback -->
#             <col style="width: 15%;">  <!-- status-->
#         </colgroup>
#         '''
#     )

#     # Tampilkan HTML ke Streamlit
#     st.markdown(table_style, unsafe_allow_html=True)
#     st.markdown(table_html, unsafe_allow_html=True)

# # Untuk menjalankan langsung saat dijalankan sebagai script utama
# if __name__ == "__main__":
#     listqa_page()


import streamlit as st
import pandas as pd
from db_connection  import get_connection
from datetime import datetime


def fetch_data():
    conn = get_connection()
    curr = conn.cursor()
    curr.execute("SELECT * FROM mtlogquestionuser")
    rows = curr.fetchall()
    conn.close()
    print("rows",rows)
    return rows

def listqa_page():
    # Judul aplikasi
    st.title("Log User Question")

    result = fetch_data()
    print("result fetch data",result)

    if not result:
        st.warning("Belum ada pertanyaan yang masuk.")
        return

    cid,member_names, questions, answers, dates,userfeedback,guideanswer,topicquestion,subtopicquestion = zip(*result)  # Unpacking hasil 
    dates_only = [datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f").date() for d in dates]

    
    # Insert data
    data = {

        "dates":dates_only,
        "Topic question":list(topicquestion),
        "Sub topic question":list(subtopicquestion),
        "Name": list(member_names),
        "Question": list(questions),
        "Answer": list(answers),
        "Suggestion":list(guideanswer)
    }


    # Membuat DataFrame
    df = pd.DataFrame(data)

    # Menampilkan tabel
    table_style = """
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
                text-align: left;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 10px;
            }
            th {
                background-color: #777;
                color: white;
            }
        </style>
    """
    st.markdown(table_style, unsafe_allow_html=True)
    st.dataframe(df, hide_index=True)
