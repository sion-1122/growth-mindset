import streamlit as st
import pandas as pd
from utils.project_tasks import (
    initialize_files,
    load_projects,
    add_project,
    get_tasks_for_project,
    Project,
    load_projects_for_user
)


def show():
    initialize_files()
    st.title("📂 Project Management")
    st.write("Manage your projects here.")

    # Get current user's ID from session state
    current_user = st.session_state.get("user_id")

    st.header("Add a new Project")

    if(st.button("Add Project")):
        @st.dialog("Add a new Project" )
        def add_project_dialog():
            with st.form("new_project_form"):
                project_name: str = st.text_input("Project Name")
                # Text area for a detailed project description
                project_description: str = st.text_area("Project Description")
                # Dropdown to select project status
                project_status: str = st.selectbox("Project Status", ["Not Started", "In Progress", "Completed"])
                # Optional start date input (user can leave empty)
                project_start_date: str = st.date_input("Start Date (YYYY-MM-DD)")
                # Optional end date input
                project_end_date: str = st.date_input("End Date (YYYY-MM-DD)")

                submitted = st.form_submit_button("Add Project")

                if(submitted):
                    project_df = load_projects()
                    new_id = int(project_df["project_id"].max() + 1) if not project_df.empty else 1

                    new_project = Project(
                        project_id=new_id,
                        name=project_name,
                        description=project_description,
                        status=project_status,
                        user_id=current_user,
                        start_date=project_start_date if project_start_date else None,
                        end_date=project_end_date if project_end_date else None,
                    )

                    add_project(new_project)

                    st.success("Project added successfully!")
                    st.rerun()
        add_project_dialog()
    st.header("Your Projects")

    # Load only current user's projects
    project_df = load_projects_for_user(current_user)

    if project_df.empty:
        st.info("No projects found. Please add a project above.")
    else:
        num_cols: int = 3  # For example, 3 cards per row.
        cols = st.columns(num_cols)
        for idx, (_, row) in enumerate(project_df.iterrows()):
            col = cols[idx % num_cols]
            with col.container(border=True):
                st.markdown(f"### {row['name']}")
                st.write(row["description"])
                st.write(f"**Status:** {row['status']}")
                st.write(f"**Start Date:** {row.get('start_date', 'N/A')}")
                st.write(f"**End Date:** {row.get('end_date', 'N/A')}")

                if st.button("View Details", key=f"view_{row['project_id']}"):
                    @st.dialog("Project Details")
                    def project_details_dialog():
                        with st.container(border=False):
                            st.write(f"**Project ID:** {row['project_id']}")
                            st.write(f"**Description:** {row['description']}")
                            st.write(f"**Status:** {row['status']}")
                            st.write(f"**Start Date:** {row.get('start_date', 'N/A')}")
                            st.write(f"**End Date:** {row.get('end_date', 'N/A')}")
                            st.subheader("Tasks for this Project")
                            tasks_df: pd.DataFrame = get_tasks_for_project(row['project_id'])
                            if tasks_df.empty:
                                st.info("No tasks found for this project.")
                            else:
                                st.dataframe(tasks_df)

                    project_details_dialog()
