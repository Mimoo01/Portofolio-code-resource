import streamlit as st
from db_connection import get_connection

# Koneksi ke database PostgreSQL
conn = get_connection()
cur = conn.cursor()

def signup():
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>Sign Up Admin</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    back_button = st.button("Back to Login" )

    with st.form("signup_form"):
        name = st.text_input("Name")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Register",type="primary",use_container_width=True)

        if submitted:
            # Cek apakah username atau email sudah digunakan
            cur.execute("SELECT * FROM mtadmin WHERE cusername = %s OR cemail = %s", (username, email))
            if cur.fetchone():
                st.warning("Username atau email sudah terdaftar.")
            else:
                cur.execute(
                    "INSERT INTO mtadmin (cname, cusername, cpassword, cemail) VALUES (%s, %s, %s, %s)",
                    (name, username, password, email)
                )
                conn.commit()
                st.success("Registrasi berhasil! Silakan kembali ke halaman login.")
        if back_button:
            st.session_state.page = "login"
            st.rerun()

