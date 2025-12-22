from httpx import get
from narwhals import col
from onnx import save
from regex import F
import streamlit as st
from torch import ge
from db_connection import get_connection
from transformers import AutoTokenizer
from sentence_transformers import SentenceTransformer
from savedb import save_data

def getsubtopic ():
    try:
        conn = get_connection()
        with conn.cursor() as curr:
            curr.execute("SELECT DISTINCT cknowledgesubtopic FROM mtknowledgebase")
            subtopics = [row[0] for row in curr.fetchall()]
        return subtopics
    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil subtopik: {e}")
        return []
    
def insertmtfield(ctopicfield,csubtopicfield,clabelfield,ctypefield,idfield,ctopictemplatefield):
    try:
        conn = get_connection()
        with conn.cursor() as curr:
            curr.execute(
                "INSERT INTO mtlistfield (ctopicfield, csubtopicfield, clabelfield, ctypefield,cidfield,ctopictemplatefield) VALUES (%s, %s, %s, %s,%s,%s)",
                (ctopicfield, csubtopicfield, clabelfield, ctypefield,idfield,ctopictemplatefield)
            )
        conn.commit()
        print("Data berhasil disimpan ke mtcustomfield")
    except Exception as e:
        print(f"Terjadi kesalahan saat menyimpan data: {e}")
    finally:
        conn.close()


def main():
    # Inisialisasi state
    getreset = st.session_state.get("reset_session", False)
    if "cknowledgetopictemplate" not in st.session_state:
        st.session_state.cknowledgetopictemplate = None
    if "label_cf1" not in st.session_state or getreset == True:
        st.session_state.label_cf1 = "Custom Field 1"
    if "label_cf2" not in st.session_state or getreset == True:
        st.session_state.label_cf2 = "Custom Field 2"
    if "label_cf3" not in st.session_state or getreset == True:
        st.session_state.label_cf3 = "Custom Field 3"
    if "label_cf4" not in st.session_state or getreset == True:
        st.session_state.label_cf4 = "Custom Field 4"
    if "label_cf5" not in st.session_state or getreset == True:
        st.session_state.label_cf5 = "Custom Field 5"
    if "label_cf6" not in st.session_state or getreset == True:
        st.session_state.label_cf6 = "Custom Field 6"
    if "label_cf7" not in st.session_state or getreset == True:
        st.session_state.label_cf7 = "Custom Field 7"
    if "label_cf8" not in st.session_state or getreset == True:
        st.session_state.label_cf8 = "Custom Field 8"
    if "label_cf9" not in st.session_state or getreset == True:
        st.session_state.label_cf9 = "Custom Field 9"


    if "show_input_cf1" not in st.session_state:
        st.session_state.show_input_cf1 = False
    if "show_input_cf2" not in st.session_state:
        st.session_state.show_input_cf2 = False
    if "show_input_cf3" not in st.session_state:
        st.session_state.show_input_cf3 = False
    if "show_input_cf4" not in st.session_state:
        st.session_state.show_input_cf4 = False
    if "show_input_cf5" not in st.session_state:
        st.session_state.show_input_cf5 = False
    if "show_input_cf6" not in st.session_state:
        st.session_state.show_input_cf6 = False
    if "show_input_cf7" not in st.session_state:
        st.session_state.show_input_cf7 = False
    if "show_input_cf8" not in st.session_state:
        st.session_state.show_input_cf8 = False
    if "show_input_cf9" not in st.session_state:
        st.session_state.show_input_cf9 = False

    cknowledgetopic = st.session_state.cknowledgetopic
    cknowledgesubtopic = st.session_state.cknowledgesubtopic
    clabelfield = []
    ctypefield = []
    idfield = []
    cknowledgeinformation = ()

    cknowledgetopictemplate = st.session_state.cknowledgetopictemplate

    backtoaddtopic = st.button("Back to Add Topic", use_container_width=True)
    if backtoaddtopic:
        st.session_state.cknowledgetopictemplate = None
        st.session_state.statuspage = "mainpage"
        st.session_state.reset_session = True
        st.rerun()

    st.title(f"Custom Field {cknowledgetopictemplate} template")

    if cknowledgetopictemplate == "FAQ":

        # --- Custom Field 2 ---
        col1, col2 = st.columns([10, 1])
        with col1:
            # st.session_state.customfield1 = st.text_input(
            # label=st.session_state.label_cf1,
            # value=st.session_state.customfield1,
            # key="input_cf1"
            # )
            st.session_state.cfield1 = st.text_input(
                label= st.session_state.label_cf1,
                value = st.session_state.get("cfield1", ""),
            )
        with col2:
            if st.button("✏️", key="edit_cf1"):
                st.session_state.show_input_cf1 = True

        # Tampilkan input tambahan jika tombol pensil ditekan
        if st.session_state.show_input_cf1:
            new_label_cf1 = st.text_input(st.session_state.label_cf1, placeholder="Custom Field 2")
            save_cf1 = st.button("Simpan perubahan judul custom field 1", key="save_cf1")
            if save_cf1:
                st.session_state.label_cf1 = new_label_cf1
                st.session_state.show_input_cf1 = False
                st.session_state.reset_session = False;
                st.success("Judul Custom Field 1 berhasil diubah!")
                st.rerun()
            # Kamu bisa simpan ini ke state juga kalau ingin pakai

        # --- Custom Field 2 ---
        col3, col4 = st.columns([10, 1])
        with col3:

            st.session_state.cfield2 = st.text_area(
                label= st.session_state.label_cf2,
                value=st.session_state.get("cfield2", ""),
            )
            # st.session_state.customfield2 = customfield2
        with col4:
            if st.button("✏️", key="edit_cf2"):
                st.session_state.show_input_cf2 = True

        if st.session_state.show_input_cf2:
            new_label_cf2 = st.text_input("Ubah judul Custom Field 2", placeholder="Custom Field 3")
            save_cf2 = st.button("Simpan perubahan judul custom field 2", key="save_cf2")
            if save_cf2:
                st.session_state.label_cf2 = new_label_cf2
                st.session_state.show_input_cf2 = False
                st.session_state.reset_session = False;
                st.success("Judul Custom Field 2 berhasil diubah!")
                st.rerun()
        idfield = ["Custom Field 1", "Custom Field 2"]
        clabelfield = [st.session_state.label_cf1, st.session_state.label_cf2]
        cknowledgeinformation = (
            f"{st.session_state.label_cf1} : {st.session_state.cfield1}.\n"
            f"{st.session_state.label_cf2} : {st.session_state.cfield2}.\n"
        )
        
        print("clabelfield FAQ", clabelfield)
        ctypefield = ["textinput", "textarea"]

            # Bisa juga kamu simpan ke state untuk digunakan nantinya
    if cknowledgetopictemplate == "Agent Knowledge":
                # --- Custom Field 2 ---
        col1, col2 = st.columns([10, 1])
        with col1:
            st.session_state.cfield1 = st.text_input(
                label= st.session_state.label_cf1,
                value=st.session_state.get("cfield1", ""),
                key="input_cf1_main"
            )
            # st.session_state.cknowledgetopicinformation = cknowledgetopicinformation
        with col2:
            if st.button("✏️", key="edit_cf1"):
                st.session_state.show_input_cf1 = True

        # Tampilkan input tambahan jika tombol pensil ditekan
        if st.session_state.show_input_cf1:
            new_label_cf1 = st.text_input("Ubah judul Custom Field 1", placeholder="Custom Field 2")
            save_cf1 = st.button("Simpan perubahan judul custom field 1", key="save_cf1")
            if save_cf1:
                st.session_state.label_cf1 = new_label_cf1
                st.session_state.show_input_cf1 = False
                st.session_state.reset_session = False;
                st.success("Judul Custom Field 1 berhasil diubah!")
                st.rerun()
            # Kamu bisa simpan ini ke state juga kalau ingin pakai

        # --- Custom Field 3 ---
        col3, col4 = st.columns([10, 1])
        with col3:
            st.session_state.cfield2 = st.text_area(
                label= st.session_state.label_cf2,
                value=st.session_state.get("cfield2", ""),
                key="input_cf2_main"
            )
        with col4:
            if st.button("✏️", key="edit_cf2"):
                st.session_state.show_input_cf2 = True

        if st.session_state.show_input_cf2:
            new_label_cf2 = st.text_input("Ubah judul Custom Field 2", placeholder="Custom Field 3")
            save_cf2 = st.button("Simpan perubahan judul custom field 2", key="save_cf2")
            if save_cf2:
                st.session_state.label_cf2 = new_label_cf2
                st.session_state.show_input_cf2 = False
                st.session_state.reset_session = False;
                st.success("Judul Custom Field 2 berhasil diubah!")
                st.rerun()
        col5, col6 = st.columns([10, 1])
        with col5:
            st.session_state.cfield3 = st.text_input(
                label= st.session_state.label_cf3,
                value=st.session_state.get("cfield3", ""),
                key="input_cf3_main"
            )

        with col6:
            if st.button("✏️", key="edit_cf3"):
                st.session_state.show_input_cf3 = True
        if st.session_state.show_input_cf3:
            new_label_cf3 = st.text_input("Ubah judul Custom Field 3", placeholder="Custom Field 3")
            save_cf3 = st.button("Simpan perubahan judul custom field 3", key="save_cf3")
            if save_cf3:
                st.session_state.label_cf3 = new_label_cf3
                st.session_state.show_input_cf3 = False
                st.session_state.reset_session = False;
                st.success("Judul Custom Field 1 berhasil diubah!")
                st.rerun()
        idfield = ["Custom Field 1", "Custom Field 2", "Custom Field 3"]
        clabelfield = [st.session_state.label_cf1, st.session_state.label_cf2, st.session_state.label_cf3]
        cknowledgeinformation = (
            f"{st.session_state.label_cf1} : {st.session_state.cfield1}.\n"
            f"{st.session_state.label_cf2} : {st.session_state.cfield2}.\n"
            f"{st.session_state.label_cf3} : {st.session_state.cfield3}.\n"
        )
        print("clabelfield Agent knowledge", clabelfield)
        ctypefield = ["textinput", "textarea", "textinput"]
        
    if cknowledgetopictemplate == "Product Knowledge":
            if "product_section" not in st.session_state:
                st.session_state.product_section = 1
            if st.session_state.product_section == 1:
                    st.subheader("New information section 1")
                    col1, col2 = st.columns(2)
                    with col1:
                        # Baris 1
                        r1col1, r1col2 = st.columns([4, 1])
                        with r1col1:
                            st.session_state.cfield1 = st.text_input(st.session_state.label_cf1, value = st.session_state.get("cfield1", ""))
                        with r1col2:
                            if st.button("✏️", key="btn_cfield1"):
                                st.session_state.show_input_cf1 = True
                        if st.session_state.show_input_cf1:
                            new_label_cf1 = st.text_input("Ubah judul Custom Field 1 product", placeholder="Custom Field 2")
                            save_cf1 = st.button("Simpan perubahan judul custom field 1", key="save_cf1")
                            if save_cf1:
                                st.session_state.label_cf1 = new_label_cf1
                                st.session_state.show_input_cf1 = False
                                st.session_state.reset_session = False
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()
                        # Baris 2
                        r2col1, r2col2 = st.columns([4, 1])
                        with r2col1:
                            st.session_state.cfield2 = st.text_input(st.session_state.label_cf2, value = st.session_state.get("cfield2", ""))
                        with r2col2:
                            if st.button("✏️", key="btn_cfield2"):
                                st.session_state.show_input_cf2 = True

                        if st.session_state.show_input_cf2:
                            new_label_cf2 = st.text_input("Ubah judul Custom Field 2", placeholder="Custom Field 3")
                            save_cf2 = st.button("Simpan perubahan judul custom field 2", key="save_cf2")
                            if save_cf2:
                                st.session_state.label_cf2 = new_label_cf2
                                st.session_state.show_input_cf2 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 2 berhasil diubah!")
                                st.rerun()

                        # Baris 3
                        r3col1, r3col2 = st.columns([4, 1])
                        with r3col1:
                            st.session_state.cfield3 = st.text_input(st.session_state.label_cf3,value = st.session_state.get("cfield3", ""))
                        with r3col2:
                            if st.button("✏️", key="btn_cfield3"):
                                st.session_state.show_input_cf3 = True

                        if st.session_state.show_input_cf3:
                            new_label_cf3 = st.text_input("Ubah judul Custom Field 3", placeholder="Custom Field 3")
                            save_cf3 = st.button("Simpan perubahan judul custom field 3", key="save_cf3")
                            if save_cf3:
                                st.session_state.label_cf3 = new_label_cf3
                                st.session_state.show_input_cf3 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()

                    with col2:
                        # Baris 4
                        r4col1, r4col2 = st.columns([4, 1])
                        with r4col1:
                            st.session_state.cfield4 = st.text_input(st.session_state.label_cf4,value = st.session_state.get("cfield4", ""))
                        with r4col2:
                            if st.button("✏️", key="btn_cfield4"):
                                st.session_state.show_input_cf4 = True

                        if st.session_state.show_input_cf4:
                            new_label_cf4 = st.text_input("Ubah judul Custom Field 4", placeholder="Custom Field 4")
                            save_cf4 = st.button("Simpan perubahan judul custom field 4", key="save_cf4")
                            if save_cf4:
                                st.session_state.label_cf4 = new_label_cf4
                                st.session_state.show_input_cf4 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()

                        # Baris 5
                        r5col1, r5col2 = st.columns([4, 1])
                        with r5col1:
                            st.session_state.cfield5 = st.text_input(st.session_state.label_cf5, value = st.session_state.get("cfield5", ""))
                        with r5col2:
                           if  st.button("✏️", key="btn_cfield5"):
                                st.session_state.show_input_cf5 = True

                        if st.session_state.show_input_cf5:
                            new_label_cf5 = st.text_input(st.session_state.label_cf5, placeholder="Custom Field 5")
                            save_cf5 = st.button("Simpan perubahan judul custom field 5", key="save_cf5")
                            if save_cf5:
                                st.session_state.label_cf5 = new_label_cf5
                                st.session_state.show_input_cf5 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()

                        # Baris 6
                        r6col1, r6col2 = st.columns([4, 1])
                        with r6col1:
                            st.session_state.cfield6 = st.text_input(st.session_state.label_cf6,value= st.session_state.get("cfield6", ""))
                        with r6col2:
                            if st.button("✏️", key="btn_cfield6"):
                                st.session_state.show_input_cf6 = True

                        if st.session_state.show_input_cf6:
                            new_label_cf6 = st.text_input(st.session_state.label_cf6, placeholder="Custom Field 6")
                            save_cf6 = st.button("Simpan perubahan judul custom field 6", key="save_cf6")
                            if save_cf6:
                                st.session_state.label_cf6 = new_label_cf6
                                st.session_state.show_input_cf6 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()

                    if st.button("Next ➡️", use_container_width=True):
                        st.session_state.product_section = 2
                        st.rerun()
            elif st.session_state.product_section == 2:
                        col1, col2 = st.columns([10, 1])
                        with col1:
                            st.session_state.cfield7 = st.text_area(
                                label= st.session_state.label_cf7,
                                value=st.session_state.get("cfield7", "")
                            )
                            # st.session_state.cknowledgetopicinformation = cknowledgetopicinformation
                        with col2:
                            if st.button("✏️", key="edit_cf1"):
                                st.session_state.show_input_cf7 = True

                        # Tampilkan input tambahan jika tombol pensil ditekan
                        if st.session_state.show_input_cf7:
                            new_label_cf7 = st.text_input("Ubah judul Custom Field 7", placeholder="Custom Field 2")
                            save_cf7 = st.button("Simpan perubahan judul custom field 7", key="save_cf7")
                            if save_cf7:
                                st.session_state.label_cf7 = new_label_cf7
                                st.session_state.show_input_cf7 = False
                                st.success("Judul Custom Field 7 berhasil diubah!")
                                st.rerun()
                            # Kamu bisa simpan ini ke state juga kalau ingin pakai

                        # --- Custom Field 3 ---
                        col3, col4 = st.columns([10, 1])
                        with col3:
                            st.session_state.cfield8 = st.text_area(
                                label= st.session_state.label_cf8,
                                value=st.session_state.get("cfield8", ""),
                            )
                        with col4:
                            if st.button("✏️", key="edit_cf2"):
                                st.session_state.show_input_cf8 = True

                        if st.session_state.show_input_cf8:
                            new_label_cf8 = st.text_input("Ubah judul Custom Field 8", placeholder="Custom Field 8")
                            save_cf8 = st.button("Simpan perubahan judul custom field 8", key="save_cf8")
                            if save_cf8:
                                st.session_state.label_cf8 = new_label_cf8
                                st.session_state.show_input_cf8 = False
                                st.success("Judul Custom Field 2 berhasil diubah!")
                                st.rerun()
                        col5, col6 = st.columns([10, 1])
                        with col5:
                            st.session_state.cfield9 = st.text_area(
                                label= st.session_state.label_cf9,
                                value=st.session_state.get("cfield9", ""),
                            )
                        with col6:
                            if st.button("✏️", key="edit_cf9"):
                                st.session_state.show_input_cf9 = True
                        if st.session_state.show_input_cf9:
                            new_label_cf9 = st.text_input("Ubah judul Custom Field 9", placeholder="Custom Field 9")
                            save_cf9 = st.button("Simpan perubahan judul custom field 9", key="save_cf9")
                            if save_cf9:
                                st.session_state.label_cf9 = new_label_cf9
                                st.session_state.show_input_cf9 = False
                                st.session_state.reset_session = False;
                                st.success("Judul Custom Field 1 berhasil diubah!")
                                st.rerun()
            idfield = ["Custom Field 1", "Custom Field 2", "Custom Field 3", "Custom Field 4", "Custom Field 5", "Custom Field 6","Custom Field 7","Custom Field 8", "Custom Field 9"]
            clabelfield = [st.session_state.label_cf1, st.session_state.label_cf2, st.session_state.label_cf3, st.session_state.label_cf4, st.session_state.label_cf5, st.session_state.label_cf6, st.session_state.label_cf7, st.session_state.label_cf8, st.session_state.label_cf9]
            cknowledgeinformation = (
                f"{st.session_state.label_cf1} : {st.session_state.cfield1}.\n"
                f"{st.session_state.label_cf2} : {st.session_state.cfield2}.\n"
                f"{st.session_state.label_cf3} : {st.session_state.cfield3}.\n"
                f"{st.session_state.label_cf4} : {st.session_state.cfield4}.\n"
                f"{st.session_state.label_cf5} : {st.session_state.cfield5}.\n"
                f"{st.session_state.get('label_cf6', 'Custom Field 6')} : {st.session_state.get('cfield6', '')}.\n"
                f"{st.session_state.get('label_cf7', 'Custom Field 7')} : {st.session_state.get('cfield7', '')}.\n"
                f"{st.session_state.get('label_cf8', 'Custom Field 8')} : {st.session_state.get('cfield8', '')}.\n"
                f"{st.session_state.get('label_cf9', 'Custom Field 9')} : {st.session_state.get('cfield9', '')}.\n"
            )
            ctypefield = ["textinput", "textinput", "textinput", "textinput", "textinput", "textinput", "textarea", "textarea", "textarea"]



    col1, col2 = st.columns(2)
    with col1:
        save_clicked = st.button("Save", key="save", use_container_width=True)
        if save_clicked:
            st.session_state["save_trigger"] = True
            
    with col2:
        cancel_clicked = st.button("❌ Cancel", key="cancel_button", use_container_width=True)
        if cancel_clicked:
            st.session_state["cancel_trigger"] = True
    if "save_trigger" in st.session_state and st.session_state["save_trigger"]:
        # Simpan data ke database
        cknowledgetopictemplate = st.session_state.cknowledgetopictemplate
        cknowledgetopic = st.session_state.cknowledgetopic
        cknowledgesubtopic = st.session_state.cknowledgesubtopic
        print("clabelfield", clabelfield)
        print("cknowledgeinformation", cknowledgeinformation)
        print("ctypefield", ctypefield)
        print("idfield", idfield)
        # clabelfield = [st.session_state.label_cf1, st.session_state.label_cf2, st.session_state.label_cf3]
        # ctypefield = ["textinput", "textarea", "textinput"]
        save_data(
            cknowledgetopic,cknowledgeinformation,cknowledgetopic,cknowledgesubtopic,"addnewknowledge")
        insertmtfield(cknowledgetopic, cknowledgesubtopic, clabelfield, ctypefield,idfield,cknowledgetopictemplate)
        st.session_state.status = "listknowledgeinformation"
        if cknowledgetopictemplate == "FAQ":
            st.session_state["cfield1"], st.session_state["cfield2"] = "",""
        elif cknowledgetopictemplate == "Agent Knowledge":
            st.session_state["cfield1"],st.session_state["cfield2"],st.session_state["cfield3"] = "","",""
        elif cknowledgetopictemplate == "Product Knowledge":
            st.session_state["cfield1"],st.session_state["cfield2"],st.session_state["cfield3"],st.session_state["cfield4"],st.session_state["cfield5"],st.session_state["cfield6"],st.session_state["cfield7"],st.session_state["cfield8"],st.session_state["cfield9"] = "","","","","","","","",""
        st.session_state["cknowledgetopic"], st.session_state["cknowledgetopictempalte"],st.session_state["cknowledgetopictemplate"] = "","",""
            
        st.session_state["save_trigger"] = False
        st.session_state.statuspage = "mainpage"
        st.session_state.reset_session = True;
        st.success("Perubahan berhasil disimpan!")
        st.rerun()
# Jalankan aplikasi

if __name__ == "__main__":
    main()

