import streamlit as st
from db_connection import get_connection
import pandas as pd
from datetime import datetime, date

# Lebarkan layout halaman
st.set_page_config(layout="wide")

# Ambil koneksi DB
conn = get_connection()
curr = conn.cursor()

def fetch_data(start_date, end_date):
    conn = get_connection()
    query = """
        SELECT * FROM mtlogquestionuser 
        WHERE date::date BETWEEN %s AND %s
    """
    with conn.cursor() as curr:
        curr.execute(query, (start_date, end_date))
        rows = curr.fetchall()
    return rows

def fetch_data_ratinguser(start_date, end_date):
    conn = get_connection()
    query = """
        SELECT DISTINCT
            r.csessionid, 
            r.cuserating, 
            r.date, 
            q.cid, 
            q.cname 
        FROM mtloguserating r
        LEFT JOIN mtlogquestionuser q ON r.csessionid = q.csessionid
        WHERE r.date::date BETWEEN %s AND %s
    """
    with conn.cursor() as curr:
        curr.execute(query, (start_date, end_date))
        rows = curr.fetchall()
    return rows

def main():
    statuspage = st.session_state.get("statusdashboard", "")
    date_range = st.session_state.get("selected_date_range", None)
    
    if not date_range:
        st.error("Tanggal belum dipilih. Silakan kembali ke Dashboard.")
        return

    start_date, end_date = date_range

    if st.button("Kembali ke Dashboard"):
        st.session_state.page = "login"
        st.rerun()

    # ====== Jika statusdashboard = ratinguser ======
    if statuspage == "ratinguser":
        result = fetch_data_ratinguser(start_date, end_date)

        if not result:
            st.warning("Belum ada data rating pada rentang tanggal tersebut.")
            return

        csessionid, cuserating, dates, cuserid, cusername = zip(*result)

        dates_only = []
        for d in dates:
            if isinstance(d, datetime):
                dates_only.append(d.date())
            elif isinstance(d, date):
                dates_only.append(d)
            elif isinstance(d, str):
                try:
                    parsed_date = datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f").date()
                except ValueError:
                    parsed_date = datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date()
                dates_only.append(parsed_date)
            else:
                dates_only.append(None)

        df = pd.DataFrame({
            "Session ID": csessionid,
            "User ID": cuserid,
            "Username": cusername,
            "User Rating": cuserating,
            "Date": dates_only
        })

        selected_rating = st.selectbox("Filter berdasarkan rating:", ["Semua", "1", "2", "3", "4", "5"])
        if selected_rating != "Semua":
            df = df[df["User Rating"].astype(str) == selected_rating]

        st.dataframe(df, use_container_width=True)

    # ====== Jika statusdashboard = statistikpertanyaan ======
    elif statuspage == "statistikpertanyaan":
        result = fetch_data(start_date, end_date)

        if not result:
            st.warning("Belum ada data pada rentang tanggal tersebut.")
            return

        ids,csessionid,member_names,ctopicquestion,csubtopicquestion,questions, answers, dates,suggestion = zip(*result)

        dates_only = []
        for d in dates:
            if isinstance(d, datetime):
                dates_only.append(d.date())
            elif isinstance(d, date):
                dates_only.append(d)
            elif isinstance(d, str):
                try:
                    parsed_date = datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f").date()
                except ValueError:
                    parsed_date = datetime.strptime(d, "%Y-%m-%d %H:%M:%S").date()
                dates_only.append(parsed_date)
            else:
                dates_only.append(None)

        df = pd.DataFrame({
            "Date": dates_only,
            "Session ID": csessionid,
            "Topic question": ctopicquestion,
            "Sub topic question": csubtopicquestion,
            "Member Name": member_names,
            "Question": questions,
            "Answer": answers,
            "Suggestion": suggestion,
        })

        category_filter = st.selectbox(
            "Filter berdasarkan status pertanyaan:",
            ["Semua", "Pertanyaan dapat terjawab dengan baik", "Tidak Bisa Dijawab"]
        )
        if category_filter == "Pertanyaan dapat terjawab dengan baik":
            df = df[df["Suggestion"] == "Tidak ada saran,Pertanyaan dapat terjawab dengan baik"]
        elif category_filter == "Tidak Bisa Dijawab":
            df = df[df["Suggestion"] != "Tidak ada saran,Pertanyaan dapat terjawab dengan baik"]

        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()

