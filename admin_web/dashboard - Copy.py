import streamlit as st
import pandas as pd
import altair as alt
import psycopg2
from datetime import datetime
from seeallpage import main as seeallpage

# CSS untuk mengurangi padding atas
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

def get_data_from_db():
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
    #     password="root",
    # )
    
    with conn.cursor() as curr:
        curr.execute("SELECT cquestion, date, csuggestion FROM mtlogquestionuser")
        rows = curr.fetchall()
        df = pd.DataFrame(rows, columns=["cquestion", "date", "csuggestion"])
    
    conn.close()
    return df

def get_data_from_dbmtloguserating():
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
    #     password="root",
    # )
    with conn.cursor() as curr:
        curr.execute("SELECT csessionid, date, cuserating FROM mtloguserating")
        rows = curr.fetchall()
        df = pd.DataFrame(rows, columns=["csessionid", "date","cuserating"])
    
    conn.close()
    return df


def main():
    if st.session_state.page == "login":
        st.title("Dashboard Admin")

        df_questions = get_data_from_db()
        df_user_rating = get_data_from_dbmtloguserating()

        df_questions['date'] = pd.to_datetime(df_questions['date'])
        df_user_rating['date'] = pd.to_datetime(df_user_rating['date'])


        # Input tanggal
        start_date = st.date_input("Mulai dari tanggal", value=datetime.today().date())
        end_date = st.date_input("Sampai tanggal", value=datetime.today().date())

        if start_date > end_date:
            st.error("Tanggal mulai tidak boleh lebih besar dari tanggal sampai.")
            return

        # Filter data question
        filtered_df = df_questions[
            (df_questions['date'].dt.date >= start_date) & 
            (df_questions['date'].dt.date <= end_date)
        ]

        # Filter data rating
        filtered_rating_df = df_user_rating[
            (df_user_rating['date'].dt.date >= start_date) & 
            (df_user_rating['date'].dt.date <= end_date)
        ]

        # ==================== CHART PERTANYAAN ====================
        if not filtered_df.empty:
            filtered_df['csuggestion'] = filtered_df['csuggestion'].fillna("").astype(str).str.strip()
            filtered_df['Kategori'] = filtered_df['csuggestion'].apply(
                lambda text: "Pertanyaan dapat terjawab dengan baik"
                if text == "Tidak ada saran,Pertanyaan dapat terjawab dengan baik"
                else "Tidak Bisa Dijawab"
            )

            all_categories = ["Pertanyaan dapat terjawab dengan baik", "Tidak Bisa Dijawab"]
            df_grouped = (
                filtered_df.groupby('Kategori').size()
                .reindex(all_categories, fill_value=0)
                .reset_index(name='Jumlah')
            )

            max_jumlah = max(1, df_grouped['Jumlah'].max())
            y_ticks = list(range(0, max_jumlah + 1))

            st.markdown("### Statistik Pertanyaan Terjawab dan Tidak Terjawab")
            if st.button("See all - Pertanyaan"):
                st.session_state.selected_date_range = (start_date, end_date)
                st.session_state.page = "see_all"
                st.session_state.statusdashboard = "statistikpertanyaan"
                st.rerun()

            chart1 = alt.Chart(df_grouped).mark_bar().encode(
                x=alt.X('Kategori:N', axis=alt.Axis(title=None, labelAngle=0)),
                y=alt.Y('Jumlah:Q', title='Jumlah Pertanyaan',
                        scale=alt.Scale(domain=[0, max_jumlah]),
                        axis=alt.Axis(values=y_ticks, format="d")),
                color=alt.Color('Kategori:N', legend=alt.Legend(title="Kategori"))
            ).properties(height=300)

            st.altair_chart(chart1, use_container_width=True)
        else:
            st.info("Tidak ada data pertanyaan ditemukan pada rentang tanggal yang dipilih.")

        # ==================== CHART RATING ====================
        if not filtered_rating_df.empty:
            df_grouped_rating = (
                filtered_rating_df.groupby('cuserating').size()
                .reset_index(name='Jumlah')
                .sort_values('cuserating')
            )

            max_rating_jumlah = max(1, df_grouped_rating['Jumlah'].max())
            y_ticks_rating = list(range(0, max_rating_jumlah + 1))

            st.markdown("### Rating Tingkat Kepuasan User")
            if st.button("See all - Rating"):
                st.session_state.selected_date_range = (start_date, end_date)
                st.session_state.page = "see_all"
                st.session_state.statusdashboard = "ratinguser"
                st.rerun()

            chart2 = alt.Chart(df_grouped_rating).mark_bar().encode(
                x=alt.X('cuserating:N', title='Rating'),
                y=alt.Y('Jumlah:Q', title='Jumlah Rating',
                        scale=alt.Scale(domain=[0, max_rating_jumlah]),
                        axis=alt.Axis(values=y_ticks_rating, format="d")),
                color=alt.Color('cuserating:N', legend=alt.Legend(title="Rating"))
            ).properties(height=300)

            st.altair_chart(chart2, use_container_width=True)
        else:
            st.info("Tidak ada data rating ditemukan pada rentang tanggal yang dipilih.")
        
    elif st.session_state.page == "see_all":
        seeallpage()


if __name__ == "__main__":
    main()












