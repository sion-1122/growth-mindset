import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Tuple

# --- Helper Function to Fetch a Random Motivational Quote ---
def get_random_quote() -> Tuple[str, str]:
    """
    Fetches a random motivational quote from the Quotable API.
    Returns:
        A tuple containing the quote and the author.
    """
    try:
        response = requests.get("https://api.quotable.io/random")
        if response.status_code == 200:
            data = response.json()
            return data["content"], data["author"]
        else:
            # In case the API call fails, return a default quote.
            return "Keep pushing forward!", "Unknown"
    except Exception as e:
        # On any exception, also return a default quote.
        return "Keep pushing forward!", "Unknown"

# --- Page Configuration and Custom CSS for Aesthetic UI ---

def show():
    st.markdown(
        """
        <style>
        /* Set a light background and some padding for the main container */
        .main {
            background-color: #f5f5f5;
            padding: 20px;
        }
        /* Styling for the quote text */
        .quote {
            font-size: 1.5em;
            font-style: italic;
            color: #555;
            margin-bottom: 5px;
        }
        /* Styling for the author text */
        .author {
            text-align: right;
            font-size: 1.2em;
            color: #888;
        }
        </style>
        """, unsafe_allow_html=True
    )

    # --- Home Page Layout ---
    with st.container():
        st.title("Home Dashboard")
        st.write("Welcome to the Growth Mindset App Dashboard!")

    # --- Motivational Quote Section ---
    quote, author = get_random_quote()
    # Create two columns: one for the quote and one for analytics.
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Motivational Quote")
        st.markdown(f"<p class='quote'>\"{quote}\"</p>", unsafe_allow_html=True)
        st.markdown(f"<p class='author'>- {author}</p>", unsafe_allow_html=True)

    # --- Analytics Section ---
    with col2:
        st.markdown("### Analytics")

        # Simulate analytics: Tasks completed over the last 7 days.
        today = datetime.today()
        # Generate dates for the last 7 days.
        dates = [today - timedelta(days=i) for i in range(7)]
        dates = sorted(dates)
        data = {
            "Date": [d.strftime("%Y-%m-%d") for d in dates],
            "Tasks Completed": [5, 8, 6, 10, 7, 9, 12]  # Sample data
        }
        df_tasks = pd.DataFrame(data)
        st.markdown("#### Tasks Completed Over the Last 7 Days")
        # Display a line chart using the DataFrame.
        st.line_chart(df_tasks.set_index("Date"))

        # Additional analytics: Sample project progress.
        st.markdown("#### Project Progress")
        project_data = {
            "Project": ["Project A", "Project B", "Project C"],
            "Progress (%)": [80, 55, 90]
        }
        df_progress = pd.DataFrame(project_data)
        st.bar_chart(df_progress.set_index("Project"))

    # --- Footer Section ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.write("Keep up the great work and have an awesome day!")
