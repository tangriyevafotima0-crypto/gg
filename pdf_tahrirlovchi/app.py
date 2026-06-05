"""Streamlit UI for PDF text editor application."""

import tempfile
import os

import streamlit as st

from pdf_engine import (
    open_pdf,
    extract_text_by_page,
    count_matches,
    apply_replacements,
    get_page_count,
)
from exporters import export_as_pdf, export_as_docx, export_as_markdown, export_as_txt


def main():
    st.set_page_config(page_title="PDF Tahrirlovchi", page_icon="📄", layout="wide")
    st.title("PDF Tahrirlovchi")
    st.caption("PDF fayllarda so'z topish, almashtirish va o'chirish")

    # File upload
    uploaded_file = st.file_uploader(
        "PDF faylni yuklang",
        type=["pdf"],
        help="PDF faylni shu yerga tashlang yoki tanlang",
    )

    if uploaded_file is None:
        st.info("Iltimos, PDF fayl yuklang.")
        return

    # Read the uploaded file
    file_bytes = uploaded_file.read()

    try:
        doc = open_pdf(file_bytes)
    except Exception as e:
        st.error(f"PDF faylni ochishda xatolik: {str(e)}")
        return

    # Display document info
    page_count = get_page_count(doc)
    st.success(f"Fayl yuklandi: **{uploaded_file.name}** | Sahifalar soni: **{page_count}**")

    # Display text by page
    st.subheader("PDF matni (sahifalar bo'yicha)")
    pages_text = extract_text_by_page(doc)

    with st.expander("Sahifalarni ko'rish", expanded=False):
        for i, text in enumerate(pages_text):
            st.markdown(f"**Sahifa {i + 1}**")
            st.text_area(
                label=f"Sahifa {i + 1}",
                value=text,
                height=200,
                disabled=True,
                key=f"page_{i}",
                label_visibility="collapsed",
            )

    # Replacement settings
    st.subheader("Topish va almashtirish")

    col1, col2 = st.columns(2)
    with col1:
        case_sensitive = st.checkbox("Katta-kichik harf farqi (case-sensitive)", value=True)
    with col2:
        whole_word = st.checkbox("Faqat butun so'z (whole word)", value=False)

    # Dynamic replacement pairs
    st.markdown("**Topish va almashtirish juftliklari:**")

    if "replacement_pairs" not in st.session_state:
        st.session_state.replacement_pairs = [{"find": "", "replace": ""}]

    # Add/remove buttons
    col_add, col_remove = st.columns([1, 1])
    with col_add:
        if st.button("+ Juftlik qo'shish"):
            st.session_state.replacement_pairs.append({"find": "", "replace": ""})
            st.rerun()
    with col_remove:
        if len(st.session_state.replacement_pairs) > 1:
            if st.button("- Oxirgi juftlikni o'chirish"):
                st.session_state.replacement_pairs.pop()
                st.rerun()

    # Input fields for each pair
    replacements = []
    for idx, pair in enumerate(st.session_state.replacement_pairs):
        col_find, col_replace = st.columns(2)
        with col_find:
            find_val = st.text_input(
                f"Topish #{idx + 1}",
                value=pair["find"],
                key=f"find_{idx}",
                placeholder="Topiladigan so'z...",
            )
        with col_replace:
            replace_val = st.text_input(
                f"Almashtirish #{idx + 1}",
                value=pair["replace"],
                key=f"replace_{idx}",
                placeholder="Almashtiriluvchi so'z (bo'sh qoldirsa o'chiriladi)...",
            )
        st.session_state.replacement_pairs[idx] = {"find": find_val, "replace": replace_val}
        if find_val.strip():
            replacements.append((find_val, replace_val))

    # Show match counts
    if replacements:
        st.subheader("Mosliklar soni")
        # Re-open the doc to count matches (original state)
        original_doc = open_pdf(file_bytes)
        total_all = 0
        for find_term, replace_term in replacements:
            count = count_matches(original_doc, find_term, case_sensitive, whole_word)
            total_all += count
            action = f"→ '{replace_term}'" if replace_term else "→ (o'chiriladi)"
            st.write(f"  '{find_term}' {action}: **{count}** moslik topildi")
        original_doc.close()

        if total_all == 0:
            st.warning("Hech qanday moslik topilmadi.")
        else:
            st.info(f"Jami: **{total_all}** moslik topildi.")

            # Apply button
            if st.button("O'zgarishlarni qo'llash", type="primary"):
                try:
                    # Re-open doc fresh for applying changes
                    work_doc = open_pdf(file_bytes)
                    modified_doc = apply_replacements(
                        work_doc, replacements, case_sensitive, whole_word
                    )

                    # Store modified doc in session state
                    st.session_state.modified_doc_bytes = export_as_pdf(modified_doc)
                    st.session_state.modified_doc = modified_doc
                    modified_doc.close()
                    st.success("O'zgarishlar muvaffaqiyatli qo'llandi!")
                except Exception as e:
                    st.error(f"O'zgarishlarni qo'llashda xatolik: {str(e)}")

    # Export section
    if "modified_doc_bytes" in st.session_state and st.session_state.modified_doc_bytes:
        st.subheader("Natijani yuklab olish")

        export_format = st.selectbox(
            "Format tanlang",
            options=["PDF", "Word (.docx)", "Markdown (.md)", "TXT"],
        )

        base_name = os.path.splitext(uploaded_file.name)[0]

        try:
            # Re-open modified doc for export
            modified_doc = open_pdf(st.session_state.modified_doc_bytes)

            if export_format == "PDF":
                export_data = st.session_state.modified_doc_bytes
                file_name = f"{base_name}_tahrirlangan.pdf"
                mime = "application/pdf"
            elif export_format == "Word (.docx)":
                export_data = export_as_docx(modified_doc)
                file_name = f"{base_name}_tahrirlangan.docx"
                mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            elif export_format == "Markdown (.md)":
                export_data = export_as_markdown(modified_doc)
                file_name = f"{base_name}_tahrirlangan.md"
                mime = "text/markdown"
            else:  # TXT
                export_data = export_as_txt(modified_doc)
                file_name = f"{base_name}_tahrirlangan.txt"
                mime = "text/plain"

            modified_doc.close()

            st.download_button(
                label=f"Yuklab olish ({export_format})",
                data=export_data,
                file_name=file_name,
                mime=mime,
            )
        except Exception as e:
            st.error(f"Eksport qilishda xatolik: {str(e)}")


if __name__ == "__main__":
    main()
