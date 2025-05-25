import pandas as pd
import os
from typing import Optional


class Project:
    def __init__(self, project_id: int, name: str,  description: str, status: str, user_id: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        """
        Initializes a Project instance.

        :param project_id: Unique identifier for the project.
        :param name: Name of the project.
        :param description: Brief description of the project.
        :param status: Current status (e.g., "Not Started", "In Progress", "Completed").
        :param user_id: ID of the user who created the project
        :param start_date: Optional start date (as string).
        :param end_date: Optional end date (as string).
        """
        self.project_id = project_id
        self.name = name
        self.description = description
        self.status = status
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date


class Task:
    def __init__(self, task_id: int, project_id: int, name: str, description: str, status: str, user_id: str, due_date: Optional[str] = None) -> None:
        self.task_id = task_id
        self.project_id = project_id
        self.name = name
        self.description = description
        self.status = status
        self.user_id = user_id
        self.due_date = due_date


PROJECTS_FILE: str = "data/projects.csv"
TASKS_FILE: str = "data/tasks.csv"

def initialize_files()-> None:
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(PROJECTS_FILE):
        pd.DataFrame(columns=["project_id", "name", "description", "status", "user_id", "start_date", "end_date"]).to_csv(PROJECTS_FILE, index=False)
    if not os.path.exists(TASKS_FILE):
        pd.DataFrame(columns=["task_id","project_id", "description", "status", "due_date"]).to_csv(TASKS_FILE, index=False)


# ----------------------------
# Functions to Work with Projects
# ----------------------------


def load_projects():
    return pd.read_csv(PROJECTS_FILE)

def add_project(project: Project):
    df: pd.DataFrame = load_projects()

    new_row: dict = {
        "project_id": project.project_id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "user_id": project.user_id,
        "start_date": project.start_date,
        "end_date": project.end_date
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(PROJECTS_FILE, index=False)


def update_project(project: Project):
    df: pd.DataFrame = load_projects()

    df.loc[df["project_id"] == project.project_id, ["name", "description", "status", "start_date", "end_date"]] = [
        project.name, project.description, project.status, project.start_date, project.end_date
    ]

    df.to_csv(PROJECTS_FILE, index=False)


def load_projects_for_user(user_id: str) -> pd.DataFrame:
    df = load_projects()
    return df[df["user_id"] == user_id]


# ----------------------------
# Functions to Work with Tasks
# ----------------------------

def load_tasks() -> pd.DataFrame:
    return pd.read_csv(TASKS_FILE)

def add_task(task: Task):
    tasks = load_tasks()
    new_row = {
        "task_id": task.task_id,
        "project_id": task.project_id,
        "name": task.name,
        "description": task.description,
        "status": task.status,
        "user_id": task.user_id,
        "due_date": task.due_date
    }
    tasks = pd.concat([tasks, pd.DataFrame([new_row])], ignore_index=True)
    tasks.to_csv(TASKS_FILE, index=False)

def update_task(task: Task) -> None:
    """Update an existing task in the tasks.csv file"""
    tasks_df = load_tasks()

    # Find the task to update
    mask = tasks_df["task_id"] == task.task_id
    if not mask.any():
        raise ValueError(f"Task with ID {task.task_id} not found")

    # Update all fields of the task
    tasks_df.loc[mask, [
        "name",
        "description",
        "status",
        "due_date",
        "project_id",
        "user_id"
    ]] = [
        task.name,
        task.description,
        task.status,
        task.due_date,
        task.project_id,
        task.user_id
    ]

    # Save the updated DataFrame
    tasks_df.to_csv(TASKS_FILE, index=False)

def delete_task(task_id: int):
    df: pd.DataFrame = load_tasks()

    df = df[df["task_id"] != task_id]

    df.to_csv(PROJECTS_FILE, index=False)

def get_tasks_for_project(project_id: int) -> pd.DataFrame:
    tasks_df: pd.DataFrame = load_tasks()

    return tasks_df[tasks_df["project_id"] == project_id]

def load_tasks_for_user(user_id: str) -> pd.DataFrame:
    df = load_tasks()
    return df[df["user_id"] == user_id]
