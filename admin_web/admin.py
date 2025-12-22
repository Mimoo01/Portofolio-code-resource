import streamlit as st
from router import main as mainhome_page  # Halaman utama setelah login
from db_connection import get_connection
from signup import signup as signup_page  # Fungsi halaman signup

# Koneksi ke database
conn = get_connection()
cur = conn.cursor()

# Inisialisasi session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "page" not in st.session_state:
    st.session_state.page = "login"  # bisa bernilai "login" atau "signup"

# Fungsi login
def login():
    st.markdown(
        """ 
        <div style='text-align: center;'>
            <h1>Welcome to knowledgebase admin</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
        with col2:
            signup = st.form_submit_button("Don't have an account? Sign Up here...", use_container_width=True, type="tertiary")

    if submitted:
        cur.execute("SELECT * FROM mtadmin WHERE cusername = %s AND cpassword = %s", (username, password))
        rows = cur.fetchall()
        conn.close()

        if len(rows) > 0:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login berhasil! 🎉")
            st.rerun()
        else:
            st.error("Username atau password salah!")

    if signup:
        st.session_state.page = "signup"
        st.rerun()

# Fungsi logout
def logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

# Main app
def mainlogin():
    if st.session_state.logged_in:
        mainhome_page()
    elif st.session_state.page == "signup":
        signup_page()
    else:
        login()

# Jalankan main login
mainlogin()

# Tambahkan CSS styling tergantung halaman
if st.session_state.logged_in:
    # Style untuk halaman utama (setelah login)
    st.markdown("""
        <style>
        .main .block-container {
            max-width: 90% !important;
            padding-left: 2rem;
            padding-right: 2rem;
            padding-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

elif st.session_state.page == "login":
    # Style khusus untuk halaman login
    st.markdown("""
        <style>
        .main .block-container {
            max-width:60% !important;
            margin: auto;
            padding: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
