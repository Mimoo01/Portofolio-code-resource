import streamlit as st

def edit_profile_page():
    st.title("✏️ Edit Profile")

    # Simpan nilai default di session state agar tidak hilang saat rerun
    if "profile_data" not in st.session_state:
        st.session_state.profile_data = {
            "username": "user123",
            "name": "John Doe",
            "password": "secret123"
        }

    # Input fields
    username = st.text_input("Username", value=st.session_state.profile_data["username"])
    name = st.text_input("Name", value=st.session_state.profile_data["name"])
    password = st.text_input("Password", type="password", value=st.session_state.profile_data["password"])

    # Tombol simpan
    if st.button("💾 Save Profile", use_container_width=True):
        # Simpan perubahan ke session state (atau database Anda di sini)
        st.session_state.profile_data["username"] = username
        st.session_state.profile_data["name"] = name
        st.session_state.profile_data["password"] = password

        st.success("✅ Profil berhasil diperbarui!")


