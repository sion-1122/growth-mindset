from typing import Optional
import pandas as pd
import os

JOURNAL_FILE: str= "data/journal.csv"

class Journal:
    def __init__(
        self,
        journal_id: int,
        title: str,
        content: str,
        user_id: str,
        entry_date: Optional[str] = None  # Date as a string, e.g., "2025-03-09"
    ) -> None:
        """
        Initialize a Journal entry.

        :param journal_id: Unique identifier for the journal entry.
        :param title: Title of the journal entry.
        :param content: Main content or body of the entry.
        :param user_id: ID of the user who created the journal entry.
        :param entry_date: Optional entry date. If not provided, can be set later.
        """
        self.journal_id = journal_id
        self.title = title
        self.content = content
        self.user_id = user_id
        self.entry_date = entry_date


def initialize_files()-> None:
    if not os.path.exists("data"):
        os.makedirs("data")
    if not os.path.exists(JOURNAL_FILE):
        pd.DataFrame(columns=["journal_id", "title", "content", "entry_date", "user_id"]).to_csv(JOURNAL_FILE, index=False)




def load_journal ()-> pd.DataFrame:
    initialize_files()
    return pd.read_csv(JOURNAL_FILE)


def add_journal(journal: Journal):
    df: pd.DataFrame = load_journal()

    new_row: dict = {
        "journal_id": journal.journal_id,
        "title": journal.title,
        "content": journal.content,
        "entry_date": journal.entry_date,
        "user_id": journal.user_id
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(JOURNAL_FILE, index=False)


def update_journal(journal: Journal):
    df: pd.DataFrame = load_journal()

    df.loc[df["journal_id"] == journal.journal_id, ["title", "content", "entry_date", "user_id"]] = [
        journal.title, journal.content, journal.entry_date, journal.user_id
        ]

    df.to_csv(JOURNAL_FILE, index=False)


def delete_journal(journal_id: int):
    df: pd.DataFrame = load_journal()
    df = df[df["journal_id"] != journal_id]
    df.to_csv(JOURNAL_FILE, index=False)


def get_journal_by_id(journal_id: int) -> Journal:
    df: pd.DataFrame = load_journal()
    row: pd.Series = df[df["journal_id"] == journal_id]
    return Journal(
        journal_id=row["journal_id"],
        title=row["title"],
        content=row["content"],
        user_id=row["user_id"],
        entry_date=row["entry_date"]
    )


def load_journal_for_user(user_id: str) -> pd.DataFrame:
    df = load_journal()
    return df[df["user_id"] == user_id]
