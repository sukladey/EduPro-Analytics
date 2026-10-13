# EduPro: Learner Demographics and Course Enrollment Behavior Analysis

## 📌 Project Overview

This project analyzes learner demographics and course enrollment behavior on the EduPro online learning platform using Python, Pandas, Plotly, and Streamlit.

The objective is to understand learner characteristics, course preferences, and enrollment patterns through descriptive data analysis. The insights can support course planning, learner engagement, and inclusive education strategies.

## 🎯 Project Objectives

- Analyze the age distribution of learners.
- Understand gender participation and enrollment patterns.
- Identify the most popular course categories.
- Compare beginner, intermediate, and advanced course enrollments.
- Examine course preferences across age groups and gender.
- Build an interactive Streamlit dashboard for data exploration.

## 📊 Dataset Description

The project uses three datasets or worksheets:

### 1. Users
- UserID
- UserName
- Age
- Gender

### 2. Courses
- CourseID
- CourseName
- CourseCategory
- CourseType
- CourseLevel

### 3. Transactions
- TransactionID
- UserID
- CourseID
- TransactionDate

The datasets are integrated using `UserID` and `CourseID`.

## 🛠️ Technologies Used

- **Python** — programming language
- **Pandas** — data cleaning and analysis
- **Streamlit** — interactive web dashboard
- **Plotly** — interactive charts
- **OpenPyXL** — Excel workbook support

## 📈 Dashboard Features

- Learner demographic overview
- Age-group distribution
- Gender distribution
- Course category popularity
- Course level and type analysis
- Age-group versus course-category heatmap
- Interactive demographic and course filters
- CSV export of filtered analysis

## 📁 Project Structure

```text
EduPro_GoogleSheets_Project/
│
├── app.py
├── requirements.txt
├── README.md
└── EduPro Online Platform.xlsx
```

The Excel workbook is optional in the repository if the app allows users to upload it through the dashboard.

## ⚙️ Installation and Setup

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/EduPro_GoogleSheets_Project.git
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Open the project folder

```bash
cd EduPro_GoogleSheets_Project
```

### Step 3: Install the required packages

```bash
python -m pip install -r requirements.txt
```

### Step 4: Run the Streamlit application

```bash
python -m streamlit run app.py
```

Open the local URL displayed in the terminal to access the dashboard.

## 📋 Key Performance Indicators

- Total registered learners
- Total course enrollments
- Learners with enrollments
- Enrollment distribution by age group
- Gender participation
- Course category popularity
- Course level preference
- Average enrollments per active learner

## 🔍 Analytical Methodology

1. Load the dataset.
2. Validate required columns and data consistency.
3. Clean and prepare the data.
4. Join users, courses, and transactions.
5. Create age groups.
6. Calculate enrollment metrics.
7. Visualize patterns using interactive charts.
8. Interpret results and develop descriptive recommendations.

## 💡 Expected Outcomes

The analysis helps identify which learner groups are represented on the platform, which categories attract the most enrollments, and how course preferences vary across demographic segments.

Recommendations should be based on the actual analysis results rather than assumptions.

## 🔒 Data Privacy

Learner data should be handled responsibly. Do not publish real names, email addresses, or other personally identifiable information in a public repository. Use anonymized or synthetic sample data when sharing the project publicly.

## 🚀 Future Enhancements

- Publish the dashboard online using Streamlit Community Cloud.
- Add more detailed enrollment trends over time.
- Improve data-quality reporting.
- Include downloadable charts and analytical reports.

## 👩‍💻 Project Purpose

This project focuses on descriptive learner intelligence for data-informed education planning. It does not aim to predict learner behavior or monetize personal information.