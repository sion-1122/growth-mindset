import streamlit as st
import pandas as pd
from utils.project_tasks import (
    initialize_files,
    load_projects,
    load_tasks,
    add_task,
    update_task,
    Task,  # Task class includes: task_id, project_id, name, description, status, due_date
    load_projects_for_user,
    load_tasks_for_user
)
from datetime import date
from typing import Optional
import time

def show() -> None:
    # Initialize CSV files and necessary folders.
    initialize_files()

    current_user = st.session_state.get("user_id")

    # Set the title and description for the Task Management page.
    st.title("📋 Task Management")
    st.write("Here you can manage your tasks.")

    # Load only current user's projects and tasks
    projects_df = load_projects_for_user(current_user)
    tasks_df = load_tasks_for_user(current_user)

    if projects_df.empty:
        st.error("No projects available. Please add a project first in the Projects section.")
        return

    # Add New Task Button
    if st.button("Add Task"):
        @st.dialog("Add a new Task")
        def add_task_modal() -> None:
            with st.form("new_task_form"):
                selected_project_id = st.selectbox(
                    "Select Project",
                    options=projects_df["project_id"].tolist(),
                    format_func=lambda x: projects_df[projects_df["project_id"] == x]["name"].iloc[0]
                )

                task_name = st.text_input("Task Name")
                task_description = st.text_area("Task Description")
                task_status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"])
                task_due_date = st.date_input("Due Date")

                submitted = st.form_submit_button("Add Task")

                if submitted:
                    tasks_df = load_tasks()
                    new_task_id = int(tasks_df["task_id"].max() + 1) if not tasks_df.empty else 1

                    new_task = Task(
                        task_id=new_task_id,
                        project_id=selected_project_id,
                        name=task_name,
                        description=task_description,
                        status=task_status,
                        user_id=current_user,
                        due_date=str(task_due_date) if task_due_date else None
                    )
                    add_task(new_task)
                    st.success("Task added successfully!")
                    st.rerun()

    # Display Tasks in Cards
    st.header("Your Tasks")

    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        selected_project = st.selectbox(
            "Filter by Project",
            ["All Projects"] + projects_df["name"].tolist()
        )
    with col2:
        selected_status = st.selectbox(
            "Filter by Status",
            ["All Statuses", "Not Started", "In Progress", "Completed"]
        )

    # Filter tasks based on selection
    filtered_tasks = tasks_df.copy()
    if selected_project != "All Projects":
        project_id = projects_df[projects_df["name"] == selected_project]["project_id"].iloc[0]
        filtered_tasks = filtered_tasks[filtered_tasks["project_id"] == project_id]
    if selected_status != "All Statuses":
        filtered_tasks = filtered_tasks[filtered_tasks["status"] == selected_status]

    # Display tasks in a grid
    if not filtered_tasks.empty:
        cols = st.columns(3)
        for idx, task in filtered_tasks.iterrows():
            with cols[idx % 3]:
                # Get project name for the task
                project_name = projects_df[projects_df['project_id'] == task['project_id']]['name'].iloc[0]

                # Status color mapping
                status_colors = {
                    "Not Started": "#FFE5E5",  # Light red
                    "In Progress": "#E5F6FF",  # Light blue
                    "Completed": "#E5FFE5"     # Light green
                }
                status_color = status_colors.get(task['status'], '#FFFFFF')

                # Format due date
                due_date = pd.to_datetime(task['due_date']).strftime('%Y-%m-%d') if pd.notna(task['due_date']) else 'No due date'

                # Card UI with better styling
                st.markdown(f"""
                <div style="
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 10px 0;
                    background-color: {status_color};
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                ">
                    <h3 style="margin: 0 0 10px 0; color: #333;">{task['name']}</h3>
                    <div style="
                        background-color: white;
                        border-radius: 4px;
                        padding: 10px;
                        margin-bottom: 10px;
                    ">
                        <p style="margin: 0 0 5px 0;"><strong>🏢 Project:</strong> {project_name}</p>
                        <p style="margin: 0 0 5px 0;"><strong>📊 Status:</strong> {task['status']}</p>
                        <p style="margin: 0 0 5px 0;"><strong>📅 Due:</strong> {due_date}</p>
                        <p style="margin: 0; color: #666;"><strong>📝 Description:</strong><br>{task['description']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Update button with better styling
                if st.button("✏️ Edit", key=f"update_task_{task['task_id']}",
                           use_container_width=True):
                    show_update_dialog(task, current_user)
    else:
        st.info("No tasks found matching the selected filters.")

def show_update_dialog(task: pd.Series, current_user: str):
    """Separate function to handle the update dialog"""
    # Create dialog using st.dialog
    @st.dialog("Update Task")
    def update_task_dialog():
        with st.form(f"update_task_form_{task['task_id']}"):
            st.subheader(f"Update Task: {task['name']}")

            # Form fields with better layout
            updated_name = st.text_input("Task Name",
                                    value=task['name'],
                                    placeholder="Enter task name")

            updated_description = st.text_area("Description",
                                            value=task['description'],
                                            placeholder="Enter task description",
                                            height=100)

            col1, col2 = st.columns(2)
            with col1:
                # Fix status selection by handling potential unknown status
                status_options = ["Not Started", "In Progress", "Completed"]
                current_status = task['status']
                status_index = status_options.index(current_status) if current_status in status_options else 0

                updated_status = st.selectbox(
                    "Status",
                    status_options,
                    index=status_index
                )

            with col2:
                try:
                    default_date = pd.to_datetime(task['due_date']).date()
                except:
                    default_date = date.today()

                updated_due_date = st.date_input("Due Date", value=default_date)

            # Submit button with better styling
            submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)

            if submitted:
                try:
                    updated_task = Task(
                        task_id=task['task_id'],
                        project_id=task['project_id'],
                        name=updated_name,
                        description=updated_description,
                        status=updated_status,
                        user_id=current_user,
                        due_date=str(updated_due_date)
                    )
                    update_task(updated_task)
                    st.success("✅ Task updated successfully!")
                    time.sleep(1)  # Give user time to see the success message
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating task: {str(e)}")

    # Call the dialog function
    update_task_dialog()

if __name__ == "__main__":
    show()
