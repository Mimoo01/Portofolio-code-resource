# import streamlit as st
# from streamlit_navigation_bar import st_navbar


# st.title("Ini home navbar anda")    

# page = st_navbar(["Home", "Documentation", "Examples", "Community", "About"],styles={
#     #     "nav": {
#     #     "background-color": "var(--primary-color)",
        
#     # },
#         "div":{
#             "max-width":"200rem",
#         }
# })
# st.write(page)



# if page == "Home":
#     st.header("Selamat Datang di Beranda!")
#     st.write("Ini adalah konten untuk halaman Beranda.")
# elif page == "Documentation":
#     st.header("Dokumentasi")
#     st.write("Di sini kamu akan menemukan informasi tentang aplikasi ini.")
# elif page == "Examples":
#     st.header("Contoh Penggunaan")
#     st.write("Lihat beberapa contoh bagaimana aplikasi ini dapat digunakan.")
# elif page == "Community":
#     st.header("Komunitas")
#     st.write("Bergabunglah dengan komunitas kami!")
# elif page == "About":
#     st.header("Tentang Aplikasi Ini")
#     st.write("Informasi lebih lanjut mengenai aplikasi ini.")


import streamlit as st

# Menambahkan Bootstrap Navbar dengan Markdown (HTML + CSS)
navbar = """
<style>
    .navbar {
        background-color: #343a40; /* Warna background navbar */
        padding: 10px;
    }
    .navbar a {
        color: white;
        text-decoration: none;
        padding: 14px 20px;
        font-size: 18px;
    }
    .navbar a:hover {
        background-color: #495057; /* Warna hover */
    }
</style>

<div class="navbar">
    <a href="/?page=home">Home</a>
    <a href="/?page=about">About</a>
    <a href="/?page=contact">Contact</a>
</div>
"""

# Menampilkan Navbar di atas
st.markdown(navbar, unsafe_allow_html=True)

# Mendapatkan parameter URL
query_params = st.experimental_get_query_params()
page = query_params.get("page", ["home"])[0]  # Default ke "home"

# Menampilkan halaman berdasarkan parameter URL
if page == "home":
    st.title("Halaman Home")
    st.write("Ini adalah halaman utama dengan navbar Bootstrap!")

elif page == "about":
    st.title("Tentang Kami")
    st.write("Aplikasi ini menggunakan kombinasi Streamlit + Bootstrap Navbar.")

elif page == "contact":
    st.title("Kontak Kami")
    st.write("Silakan hubungi kami di email@example.com.")

# Tambahkan elemen lainnya
st.image("https://source.unsplash.com/600x300/?technology", caption="Gambar ilustrasi")
