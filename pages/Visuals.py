import json
from pathlib import Path
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
st.set_page_config(
    page_title="Visuals",
    page_icon="📈",
)
PROJECT_PATH = Path(__file__).resolve().parent.parent
JSON_PATH = PROJECT_PATH / "data.json"
CSV_PATH = PROJECT_PATH / "data.csv"
with open(JSON_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)
months = data["months"]
exhibits = data["exhibits"]
exhibit_names = [
    exhibit["name"]
    for exhibit in exhibits
]
st.title("Data Visualizations")
st.write(data["description"])
st.header("Total Visitors by Exhibit")
totals = [
    sum(exhibit["visitors"])
    for exhibit in exhibits
]
fig, ax = plt.subplots()
ax.bar(exhibit_names, totals)
ax.set_title("Total Annual Visitors by Exhibit")
ax.set_xlabel("Exhibit")
ax.set_ylabel("Total Visitors")
plt.xticks(rotation=20)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.header("Monthly Visitors by Exhibit")
if "selected_exhibit" not in st.session_state:
    st.session_state.selected_exhibit = exhibit_names[0]
selected_name = st.selectbox(
    "Select an exhibit:",
    exhibit_names,
    key="selected_exhibit"
)
selected_exhibit = next(
    exhibit for exhibit in exhibits
    if exhibit["name"] == selected_name
)
monthly_data = pd.DataFrame({
    "Month": months,
    "Visitors": selected_exhibit["visitors"]
})
st.subheader(f"Monthly Visitors: {selected_name}")
st.line_chart(
    monthly_data,
    x="Month",
    y="Visitors",
    x_label="Month",
    y_label="Number of Visitors"
)
st.divider()
st.header("Survey Data Visualizations")
if CSV_PATH.exists() and CSV_PATH.stat().st_size > 0:

    survey_data = pd.read_csv(CSV_PATH)

    required_columns = ["Month", "Category", "Value"]

    if not all(
        column in survey_data.columns
        for column in required_columns
    ):
        st.error("The CSV file does not have the expected columns.")

    else:

        survey_data["Value"] = pd.to_numeric(
            survey_data["Value"],
            errors="coerce"
        )
        survey_data = survey_data.dropna(
            subset=required_columns
        ).copy()

        survey_data["Month"] = (
            survey_data["Month"].astype(str).str.strip()
        )
        survey_data["Category"] = (
            survey_data["Category"].astype(str).str.strip()
        )
        survey_data = survey_data[
            survey_data["Month"].isin(months)
            & (survey_data["Value"] >= 0)
        ]
        if survey_data.empty:
            st.warning(
                "There is no valid survey data available yet."
            )
        else:
            st.subheader("Total Visitors by Zone")
            category_totals = (
                survey_data.groupby("Category")["Value"]
                .sum()
                .sort_values(ascending=False)
            )
            fig, ax = plt.subplots()

            ax.bar(
                category_totals.index,
                category_totals.values
            )
            ax.set_title(
                "Total Submitted Visitor Contributions by Zone"
            )
            ax.set_xlabel("Exhibit or Zone")
            ax.set_ylabel("Total Visitor Contributions")
            plt.xticks(rotation=25, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
            st.subheader("Monthly Visitors by Zone")
            available_categories = sorted(
                survey_data["Category"].unique().tolist()
            )
            if (
                "survey_selected_category" not in st.session_state
                or st.session_state.survey_selected_category
                not in available_categories
            ):
                st.session_state.survey_selected_category = (
                    available_categories[0]
                )
            selected_category = st.selectbox(
                "Select a zone:",
                available_categories,
                key="survey_selected_category"
            )
            selected_data = survey_data[
                survey_data["Category"] == selected_category
            ]
            monthly_totals = (
                selected_data.groupby("Month")["Value"]
                .sum()
                .reindex(months)
            )
            monthly_chart_data = pd.DataFrame({
                "Month": months,
                "Visitors": monthly_totals.values
            })
            st.line_chart(
                monthly_chart_data,
                x="Month",
                y="Visitors",
                x_label="Month",
                y_label="Visitor Contributions"
            )
else:
    st.warning(
        "No survey data has been submitted yet. "
        "Visit the Survey page to add data."
    )
