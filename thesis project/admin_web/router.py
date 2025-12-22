
import streamlit as st
import psycopg2
from listknowledgenew import listknowledge_page as listknowledgepagenew
from db_connection import get_connection
from dashboard import main as dashboard_page
from editprofile import edit_profile_page as editprofilepage


def fetch_data(query):
    conn = get_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        conn.close()
        return result
    return []

def main():
    # Inisialisasi session state jika belum ada
    if "menu_visible" not in st.session_state:
        st.session_state.menu_visible = True  # Default: menu tampil

    # CSS untuk animasi smooth hide/show menu
    st.markdown(
        """
        <style>

        div.stButton > button {
        background-color: #f16522;
        color: white;
        border: none;
        height:3em;
        padding: 0.5em 1em;
        font-weight: bold;
        border-radius: 5px;
    }
        div.stButton > button:hover {
        background-color: #d4551c;  /* Warna saat hover */
        transform: scale(1.05);     /* Sedikit membesar saat hover */
        cursor: pointer;
        color:white;
    }
        .sidebar-title {
        font-size: 34px;  /* Ubah angka sesuai kebutuhan, misal 30px, 36px, dll */
        font-weight: bold;
        color: Black; /* Opsional, bisa disesuaikan */
        padding-top: 10px;
        padding-bottom: 10px;
    }


        /* Navbar tetap seperti sebelumnya */
        @media (max-width: 500px) {
            [data-testid="stSidebar"] {
                display: none;
            }
            [data-testid="collapsedControl"] {
                display: none;
            }
            [data-testid="stAppViewContainer"] {
                margin-left: 0;
            }
            #customNavbar {
                display: block;
            }
        }
        @media (min-width: 501px) {
            #customNavbar {
                display: none;
            }
        }
        #customNavbar { 
            padding: 10px 0;
            text-align: center;
        }
        #customNavbar a {
            display: block;
            color: #333;
            padding: 10px 0;
            text-decoration: none;
            font-size: 18px;
            font-weight: bold;
        }
        #customNavbar a:hover {
            background-color: #ddd;
        }

        /* Efek animasi smooth untuk menu */
        .menu-container {
            transition: max-height 0.5s ease-in-out, opacity 0.5s ease-in-out;
            overflow: hidden;
            max-height: 200px;
            opacity: 1;
        }
        .menu-hidden {
            max-height: 0;
            opacity: 0;
        }
        .content-container {
            transition: margin-top 0.5s ease-in-out;
        }
        .content-shift-up {
            margin-top: -100px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Inisialisasi session state jika belum ada
    if "screen_width" not in st.session_state:
        st.session_state.screen_width = 1000  # Nilai default

    # Gunakan komponen HTML untuk menangkap perubahan ukuran layar
    st.components.v1.html(
        """
        <script>
        function sendScreenWidth() {
            let screenWidth = window.innerWidth;
            console.log("Screen Width Updated:", screenWidth);
            
            // Kirim nilai ke Streamlit
            if (window.parent.Streamlit) {
            console.log("oke")
                window.parent.Streamlit.setComponentValue(screenWidth);
            }
        }
        window.addEventListener('resize', sendScreenWidth);
        sendScreenWidth();  // Jalankan saat pertama kali halaman dimuat
        </script>
        """,
        height=0,
    )

    # Streamlit akan menangkap nilai dari JavaScript dan memperbarui session state
    if "_component_value" in st.session_state:
        st.session_state["screen_width"] = st.session_state["_component_value"]

    # Tampilkan nilai screen width yang diperbarui secara real-time



    # Contoh: Menampilkan tombol hanya jika layar <= 500px
    if st.session_state.screen_width <= 500:
        if st.button("☰ Menu", use_container_width=True):
            st.session_state.menu_visible = not st.session_state.menu_visible

    # Tambahkan class berdasarkan status menu
    menu_class = "menu-container" if st.session_state.menu_visible else "menu-container menu-hidden"
    content_class = "content-container" if st.session_state.menu_visible else "content-container content-shift-up"

    # Navbar menu dengan animasi hide/show
    st.markdown(
        f"""
        <div id="customNavbar">
            <div class="{menu_class}">
                <a href="?menu=Home">Home</a>
                <a href="?menu=Create">Create</a>
                <a href="?menu=Read">Read</a>
                <a href="?menu=Update">Update</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )



    # Sidebar tetap ada untuk layar lebar
    with st.sidebar:
        st.markdown(f'<div class="sidebar-title">Hello, {st.session_state.username}</div>', unsafe_allow_html=True)
        
        if st.button("Dashboard", key="dashboard", use_container_width=True,type="tertiary"):
            st.session_state.menu = "dashboard"

        if st.button("Database Knowledge", key="databaseknowledge", use_container_width=True,type="tertiary"):
            st.session_state.menu = "databaseknowledge"

        if st.button("Edit password", key="editpassword", use_container_width=True,type="tertiary"):
            st.session_state.menu = "editpassword"
        if st.button("Log out", key="logout", use_container_width=True,type="tertiary"):
            st.session_state.menu = "logout"

    # Menentukan menu berdasarkan parameter URL atau sesi
    query_params = st.query_params
    if "menu" in query_params:
        st.session_state.menu = query_params["menu"][0]

    menu = st.session_state.get("menu", "dashboard")

    # Menampilkan halaman sesuai menu yang dipilih
    if menu == "dashboard":
        dashboard_page()

    elif menu == "databaseknowledge":
        # listknowledgepage()
        listknowledgepagenew()
    elif menu == "editpassword":
        editprofilepage()

    elif menu == "logout":
        st.session_state.logged_in = False
        st.session_state.menu = "Create"
        st.rerun()

if __name__ == "__main__":
    main()



