import streamlit as st
import fitz  # PyMuPDF

st.title("PDF Table of Contents Extractor (Editable Dropdown)")

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
        toc = extract_hyperlinked_toc(doc)

        if toc:
            st.subheader("Extracted Table of Contents")

            # Store editable ToC in session state
            if "edited_toc" not in st.session_state:
                st.session_state.edited_toc = {entry["id"]: entry["title"] for entry in toc}

            # ✅ Expander for editing all sections
            with st.expander("Edit Table of Contents"):
                for entry in toc:
                    new_title = st.text_input(
                        f"Edit title for Page {entry['pno_from']} - {entry['pno_to']}:",
                        value=st.session_state.edited_toc[entry["id"]],
                        key=f"title_{entry['id']}"
                    )
                    st.session_state.edited_toc[entry["id"]] = new_title  # Save changes dynamically

            # ✅ Button to "Set ToC" after editing
            if st.button("Set ToC"):
                for entry in toc:
                    entry["title"] = st.session_state.edited_toc[entry["id"]]

                # ✅ Update dropdown options with edited titles (no page numbers)
                st.session_state.dropdown_options = [entry["title"] for entry in toc]
                st.success("ToC has been updated!")

            # ✅ Dropdown below the button, showing only section names after edits
            if "dropdown_options" in st.session_state:
                selected_section = st.selectbox(
                    "Updated Sections:",
                    options=st.session_state.dropdown_options
                )

            # ✅ Display the updated ToC
            st.subheader("Updated Table of Contents")
            for entry in toc:
                edited_title = st.session_state.edited_toc[entry["id"]]
                st.write(f"**{edited_title}** (Page {entry['pno_from']}-{entry['pno_to']})")
