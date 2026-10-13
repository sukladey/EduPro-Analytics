import io
import re

import pandas as pd
import plotly.express as px
import requests
import streamlit as st


# ==================================================
# 1. CONFIGURATION
# ==================================================

SPREADSHEET_ID = "1Ts1Yjt9oiTdOeCeuJPbExNz7N3vmd0Ln"

GOOGLE_SHEET_URL = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{SPREADSHEET_ID}/export?format=xlsx"
)

st.set_page_config(
    page_title="EduPro Learner Analytics",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 EduPro Learner Analytics")
st.subheader(
    "Learner Demographics and Course Enrollment Behavior Analysis"
)
st.caption(
    "Data-driven course planning | Learner diversity | Inclusive education"
)


# ==================================================
# 2. LOAD GOOGLE SHEETS DATABASE
# ==================================================

@st.cache_data(ttl=300)
def load_google_sheets():
    response = requests.get(
        GOOGLE_SHEET_URL,
        timeout=30
    )

    response.raise_for_status()

    return pd.read_excel(
        io.BytesIO(response.content),
        sheet_name=None
    )


def normalize_name(name):
    return re.sub(
        r"[^a-z0-9]",
        "",
        str(name).strip().lower()
    )


def normalize_columns(df):
    df = df.copy()
    df.columns = [
        str(column).strip()
        for column in df.columns
    ]
    return df


def find_sheet(sheets, possible_names):
    for name, df in sheets.items():
        if normalize_name(name) in possible_names:
            return normalize_columns(df)

    return None


# ==================================================
# 3. LOAD DATABASE
# ==================================================

st.sidebar.header("Database")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel workbook if needed",
    type=["xlsx"]
)

if st.sidebar.button("Refresh database"):
    st.cache_data.clear()
    st.rerun()

try:
    if uploaded_file is not None:
        sheets = pd.read_excel(
            uploaded_file,
            sheet_name=None
        )
    else:
        sheets = load_google_sheets()

except Exception as error:
    st.error("Unable to load the Google Sheets database.")

    st.info(
        "Check the spreadsheet's viewing permissions. "
        "If the data is private, download an authorized "
        "Excel copy and upload it using the sidebar."
    )

    st.code(str(error))
    st.stop()


# ==================================================
# 4. IDENTIFY DATABASE TABLES
# ==================================================

users = find_sheet(
    sheets,
    {"user", "users", "learner", "learners"}
)

courses = find_sheet(
    sheets,
    {"course", "courses"}
)

transactions = find_sheet(
    sheets,
    {
        "transaction",
        "transactions",
        "enrollment",
        "enrollments"
    }
)

st.sidebar.caption(
    "Detected tabs: " + ", ".join(sheets.keys())
)

if users is None or courses is None or transactions is None:
    st.error(
        "The workbook must contain Users, Courses, "
        "and Transactions tabs."
    )

    st.write(
        "Tabs found:",
        list(sheets.keys())
    )

    st.markdown("""
    **Required columns**

    Users:
    - UserID
    - Age
    - Gender

    Courses:
    - CourseID
    - CourseCategory
    - CourseType
    - CourseLevel

    Transactions:
    - TransactionID
    - UserID
    - CourseID
    - TransactionDate
    """)

    st.stop()


# ==================================================
# 5. VALIDATE DATABASE COLUMNS
# ==================================================

required_columns = {
    "Users": (
        users,
        ["UserID", "Age", "Gender"]
    ),
    "Courses": (
        courses,
        [
            "CourseID",
            "CourseCategory",
            "CourseType",
            "CourseLevel"
        ]
    ),
    "Transactions": (
        transactions,
        [
            "TransactionID",
            "UserID",
            "CourseID",
            "TransactionDate"
        ]
    )
}

for table_name, (df, required) in required_columns.items():

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        st.error(
            f"{table_name} is missing columns: {missing}"
        )

        st.write(
            "Available columns:",
            list(df.columns)
        )

        st.stop()


# ==================================================
# 6. DATA CLEANING
# ==================================================

users = users.dropna(
    subset=["UserID"]
).drop_duplicates(
    subset=["UserID"]
).copy()

courses = courses.dropna(
    subset=["CourseID"]
).drop_duplicates(
    subset=["CourseID"]
).copy()

transactions = transactions.dropna(
    subset=["TransactionID"]
).drop_duplicates(
    subset=["TransactionID"]
).copy()

users["Age"] = pd.to_numeric(
    users["Age"],
    errors="coerce"
)

users.loc[
    ~users["Age"].between(0, 120),
    "Age"
] = float("nan")

transactions["TransactionDate"] = pd.to_datetime(
    transactions["TransactionDate"],
    errors="coerce"
)

# Age groups: non-overlapping categories
age_bins = [-1, 17, 25, 35, 45, float("inf")]

age_labels = [
    "<18",
    "18–25",
    "26–35",
    "36–45",
    "46+"
]

users["AgeGroup"] = pd.cut(
    users["Age"],
    bins=age_bins,
    labels=age_labels
).astype("object")

users["AgeGroup"] = users["AgeGroup"].fillna("Unknown")


# ==================================================
# 7. MERGE USERS, COURSES AND TRANSACTIONS
# ==================================================

data = transactions.merge(
    users,
    on="UserID",
    how="left"
)

data = data.merge(
    courses,
    on="CourseID",
    how="left"
)

for column in [
    "Gender",
    "AgeGroup",
    "CourseCategory",
    "CourseType",
    "CourseLevel"
]:
    data[column] = (
        data[column]
        .fillna("Unknown")
        .astype(str)
    )


# ==================================================
# 8. SIDEBAR FILTERS
# ==================================================

st.sidebar.header("Dashboard Filters")


def get_options(series):
    return [
        "All"
    ] + sorted(
        series.dropna().astype(str).unique().tolist()
    )


age_options = ["All"] + [
    group
    for group in age_labels + ["Unknown"]
    if group in data["AgeGroup"].unique()
]

selected_age = st.sidebar.selectbox(
    "Age Group",
    age_options
)

selected_gender = st.sidebar.selectbox(
    "Gender",
    get_options(data["Gender"])
)

selected_category = st.sidebar.selectbox(
    "Course Category",
    get_options(data["CourseCategory"])
)

selected_type = st.sidebar.selectbox(
    "Course Type",
    get_options(data["CourseType"])
)

selected_level = st.sidebar.selectbox(
    "Course Level",
    get_options(data["CourseLevel"])
)


filtered = data.copy()

filters = [
    ("AgeGroup", selected_age),
    ("Gender", selected_gender),
    ("CourseCategory", selected_category),
    ("CourseType", selected_type),
    ("CourseLevel", selected_level)
]

for column, selected_value in filters:

    if selected_value != "All":
        filtered = filtered[
            filtered[column].astype(str)
            == selected_value
        ]


# ==================================================
# 9. KEY PERFORMANCE INDICATORS
# ==================================================

total_enrollments = filtered[
    "TransactionID"
].nunique()

unique_learners = filtered[
    "UserID"
].nunique()

courses_per_learner = (
    filtered.groupby("UserID")["TransactionID"]
    .nunique()
)

average_courses = (
    courses_per_learner.mean()
    if not courses_per_learner.empty
    else 0
)

active_learners = int(
    (courses_per_learner >= 2).sum()
)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Enrollments",
    f"{total_enrollments:,}"
)

col2.metric(
    "Unique Learners",
    f"{unique_learners:,}"
)

col3.metric(
    "Average Enrollments per Learner",
    f"{average_courses:.2f}"
)

col4.metric(
    "Learners with 2+ Enrollments",
    f"{active_learners:,}"
)


# ==================================================
# 10. DASHBOARD TABS
# ==================================================

overview, demographics, preferences, quality = st.tabs(
    [
        "Overview",
        "Learner Demographics",
        "Course Preferences",
        "Behavior & Data Quality"
    ]
)


# ==================================================
# 11. OVERVIEW
# ==================================================

with overview:

    st.subheader("Enrollment Overview")

    col1, col2 = st.columns(2)

    age_data = (
        filtered.groupby("AgeGroup")
        .size()
        .reindex(
            age_labels + ["Unknown"],
            fill_value=0
        )
        .rename_axis("Age Group")
        .reset_index(name="Enrollments")
    )

    col1.plotly_chart(
        px.bar(
            age_data,
            x="Age Group",
            y="Enrollments",
            color="Age Group",
            title="Enrollments by Age Group"
        ),
        use_container_width=True
    )

    category_data = (
        filtered["CourseCategory"]
        .value_counts()
        .rename_axis("Course Category")
        .reset_index(name="Enrollments")
    )

    col2.plotly_chart(
        px.bar(
            category_data,
            x="Course Category",
            y="Enrollments",
            color="Course Category",
            title="Course Category Popularity"
        ),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    level_data = (
        filtered["CourseLevel"]
        .value_counts()
        .rename_axis("Course Level")
        .reset_index(name="Enrollments")
    )

    col1.plotly_chart(
        px.pie(
            level_data,
            names="Course Level",
            values="Enrollments",
            hole=0.45,
            title="Course Level Distribution"
        ),
        use_container_width=True
    )

    type_data = (
        filtered["CourseType"]
        .value_counts()
        .rename_axis("Course Type")
        .reset_index(name="Enrollments")
    )

    col2.plotly_chart(
        px.bar(
            type_data,
            x="Course Type",
            y="Enrollments",
            color="Course Type",
            title="Course Type Popularity"
        ),
        use_container_width=True
    )


# ==================================================
# 12. LEARNER DEMOGRAPHICS
# ==================================================

with demographics:

    st.subheader("Gender Distribution")

    # Use unique registered learners, not transactions.
    gender_data = (
        users["Gender"]
        .fillna("Unknown")
        .value_counts()
        .rename_axis("Gender")
        .reset_index(name="Learners")
    )

    col1, col2 = st.columns(2)

    col1.plotly_chart(
        px.pie(
            gender_data,
            names="Gender",
            values="Learners",
            hole=0.45,
            title="Registered Learners by Gender"
        ),
        use_container_width=True
    )

    age_gender = pd.crosstab(
        filtered["AgeGroup"],
        filtered["Gender"]
    ).reindex(
        age_labels + ["Unknown"],
        fill_value=0
    )

    col2.plotly_chart(
        px.imshow(
            age_gender,
            text_auto=True,
            aspect="auto",
            title="Age Group vs Gender",
            labels={
                "x": "Gender",
                "y": "Age Group",
                "color": "Enrollments"
            }
        ),
        use_container_width=True
    )

    level_gender = (
        filtered.groupby(
            ["CourseLevel", "Gender"]
        )
        .size()
        .reset_index(name="Enrollments")
    )

    st.plotly_chart(
        px.bar(
            level_gender,
            x="CourseLevel",
            y="Enrollments",
            color="Gender",
            barmode="group",
            title="Gender vs Course Level"
        ),
        use_container_width=True
    )


# ==================================================
# 13. COURSE PREFERENCES
# ==================================================

with preferences:

    st.subheader("Course Preference Analysis")

    heatmap_data = pd.crosstab(
        filtered["AgeGroup"],
        filtered["CourseCategory"]
    ).reindex(
        age_labels + ["Unknown"],
        fill_value=0
    )

    st.plotly_chart(
        px.imshow(
            heatmap_data,
            text_auto=True,
            aspect="auto",
            title="Age Group vs Course Category",
            labels={
                "x": "Course Category",
                "y": "Age Group",
                "color": "Enrollments"
            }
        ),
        use_container_width=True
    )

    col1, col2 = st.columns(2)

    col1.plotly_chart(
        px.bar(
            filtered.groupby("CourseLevel")
            .size()
            .reset_index(name="Enrollments"),
            x="CourseLevel",
            y="Enrollments",
            title="Course Level Preference"
        ),
        use_container_width=True
    )

    col2.plotly_chart(
        px.bar(
            filtered.groupby("CourseType")
            .size()
            .reset_index(name="Enrollments"),
            x="CourseType",
            y="Enrollments",
            title="Course Type Preference"
        ),
        use_container_width=True
    )

    # Avoid showing learner emails or names.
    safe_columns = [
        "TransactionDate",
        "AgeGroup",
        "Gender",
        "CourseCategory",
        "CourseType",
        "CourseLevel"
    ]

    st.subheader("Enrollment Data Preview")

    st.dataframe(
        filtered[safe_columns].head(100),
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download Filtered CSV",
        data=filtered[safe_columns].to_csv(
            index=False
        ).encode("utf-8"),
        file_name="edupro_analysis.csv",
        mime="text/csv"
    )


# ==================================================
# 14. BEHAVIOR AND DATA QUALITY
# ==================================================

with quality:

    st.subheader("Learner Behavior")

    if not courses_per_learner.empty:

        top_count = max(
            1,
            int(len(courses_per_learner) * 0.20)
        )

        sorted_counts = courses_per_learner.sort_values(
            ascending=False
        )

        total = sorted_counts.sum()

        concentration = (
            sorted_counts.head(top_count).sum() / total * 100
            if total else 0
        )

        st.write(
            f"**Enrollment share of the top 20% of learners:** "
            f"{concentration:.1f}%"
        )

        st.write(
            f"**Learners with at least two enrollments:** "
            f"{active_learners:,}"
        )

    else:
        st.info("No data matches the selected filters.")

    st.subheader("Database Quality Checks")

    quality_data = pd.DataFrame({
        "Table": [
            "Users",
            "Courses",
            "Transactions"
        ],
        "Rows after deduplication": [
            len(users),
            len(courses),
            len(transactions)
        ]
    })

    st.dataframe(
        quality_data,
        use_container_width=True,
        hide_index=True
    )

    st.write(
        "Transactions with unknown UserID:",
        int(
            (~transactions["UserID"].isin(users["UserID"]))
            .sum()
        )
    )

    st.write(
        "Transactions with unknown CourseID:",
        int(
            (~transactions["CourseID"].isin(courses["CourseID"]))
            .sum()
        )
    )

    st.write(
        "Missing learner ages:",
        int(users["Age"].isna().sum())
    )

    st.write(
        "Missing transaction dates:",
        int(transactions["TransactionDate"].isna().sum())
    )


# ==================================================
# 15. FOOTER
# ==================================================

st.divider()

st.caption(
    "EduPro | Learner Demographics and Course Enrollment "
    "Behavior Analysis. Enrollment counts do not establish "
    "course completion or learning outcomes."
)

