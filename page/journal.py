import streamlit as st
import pandas as pd
from utils.journal import (
    load_journal,
    Journal,
    initialize_files,
    add_journal,
    update_journal,
    delete_journal,
    load_journal_for_user,
)

def show():
    st.title("📖 Journal")
    st.write("Write down your thoughts and reflections here.")

    current_user = st.session_state.get("user_id")

    # ---------- Add a new Journal Entry ----------

    st.header("Add a new Journal Entry")

    with st.form("new_journal_form"):
        new_title = st.text_input("Title")
        new_content = st.text_input("Your thoughts")

        submitted = st.form_submit_button("Add entry")

        if submitted:
            initialize_files()

            journal_df = load_journal()
            new_journal_id = int(journal_df["journal_id"].max() + 1) if not journal_df.empty else 1
            new_entry = Journal(
                journal_id=new_journal_id,
                title=new_title,
                content=new_content,
                user_id=current_user,
                entry_date=str(pd.Timestamp.now().date())
            )

            add_journal(new_entry)
            st.success("Journal Entry added successfully")
            st.rerun()

    st.header("Your previous Journal entries")

    journal_df = load_journal_for_user(current_user)

    if journal_df.empty:
        st.info("No journal entries found. Add your first entry above!")
    else:
        num_cols: int = 2
        cols = st.columns(num_cols)

        for idx, (_, row) in enumerate(journal_df.iterrows()):
            col = cols[idx % num_cols]
            with col.container(border=True):
                st.markdown(f"### {row['title']}")
                st.write(row['content'])
                st.write(f"**Date:** {row['entry_date']}")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("Edit", key=f"edit_{row['journal_id']}"):
                        @st.dialog("Edit Journal Entry")
                        def edit_journal_dialog():
                            with st.form("edit_journal_form"):
                                updated_title = st.text_input("Title", value=row['title'])
                                updated_content = st.text_input("Content", value=row['content'])

                                if st.form_submit_button("Update Entry"):
                                    updated_entry = Journal(
                                        journal_id=row['journal_id'],
                                        title=updated_title,
                                        content=updated_content,
                                        user_id=current_user,
                                        entry_date=row['entry_date']
                                    )
                                    update_journal(updated_entry)
                                    st.success("Journal entry updated successfully!")
                                    st.rerun()
                        edit_journal_dialog()

                with col2:
                    if st.button("Delete", key=f"delete_{row['journal_id']}"):
                        @st.dialog("Delete Journal Entry")
                        def delete_journal_dialog():
                            st.write("Are you sure you want to delete this entry?")
                            if st.button("Confirm Delete"):
                                delete_journal(row['journal_id'])
                                st.success("Journal entry deleted successfully!")
                                st.rerun()
                        delete_journal_dialog()
