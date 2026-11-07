import csv
from pathlib import Path
import streamlit as st
import pandas as pd
CSV_PATH = Path(__file__).resolve().parent.parent / "data.csv"
CSV_HEADERS = ["Month", "Category", "Value"]
MONTHS = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

CATEGORIES = [
    "Shattered Plains Exploration",
    "Ocean Discovery",
    "Fabrial Zone",
    "Parshendi Hall",
    "Shinovari Gardens",
    "Chasmfiend Enclosure",
    "Greatshell Park"
]
def initialize_csv():
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
        return None
    with open(CSV_PATH, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        existing_headers = next(reader, None)
        has_records = next(reader, None) is not None
    if existing_headers == CSV_HEADERS:
        return None
    if existing_headers == ["Category", "Value"] and not has_records:
        with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(CSV_HEADERS)
        return None
    return (
        "The existing data.csv has an incompatible structure. "
        "Please check its headers and existing records before submitting."
    )
st.set_page_config(
    page_title="Survey",
    page_icon="📝",
)
csv_error = initialize_csv()
st.title("Rosharan Center Visitor Survey")
st.write(
    """
    Submit monthly visitor counts for the Rosharan Center's exhibits
    and zones.

    Each submission contributes to the recorded visitor totals.
    """
)
if csv_error:
    st.error(csv_error)
with st.form("survey_form"):
    month_input = st.selectbox(
        "Which month are you reporting for?",
        MONTHS
    )
    category_input = st.selectbox(
        "Which exhibit or zone are you reporting?",
        CATEGORIES
    )
    value_input = st.text_input(
        "How many visitors should be added to this month's count?"
    )
    submitted = st.form_submit_button("Submit Data")
    if submitted:
        if csv_error:
            st.error("Unable to submit data because the CSV structure is incorrect.")
        else:
            value_input = value_input.strip()
            if value_input == "":
                st.error("Please enter a visitor count.")
            else:
                try:
                    visitor_count = int(value_input)
                    if visitor_count < 0:
                        st.error("Visitor count cannot be negative.")
                    else:
                        with open(
                            CSV_PATH,
                            "a",
                            newline="",
                            encoding="utf-8"
                        ) as file:

                            writer = csv.writer(file)

                            writer.writerow([
                                month_input,
                                category_input,
                                visitor_count
                            ])

                        st.success("Your data has been submitted!")

                        st.write(
                            f"""
                            **Month:** {month_input}

                            **Category:** {category_input}

                            **Visitors:** {visitor_count}
                            """
                        )
                except ValueError:
                    st.error(
                        "Please enter a valid whole number for the visitor count."
                    )
st.divider()
st.header("Current Data in CSV")
if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:
    try:
        current_data_df = pd.read_csv(CSV_PATH)
        st.dataframe(
            current_data_df,
            use_container_width=True
        )
    except (pd.errors.ParserError, pd.errors.EmptyDataError):
        st.error("Unable to read the CSV file. Check its formatting.")
else:
    st.warning("The data.csv file is empty or does not exist yet.")
