# CodeGenesis TEAM: Comprehensive COVID-19 Data Analysis

---
# Jira Board

# **AI-Driven Risk Classification Project**

## **Overview**

This project focuses on predicting risk levels for unvaccinated individuals based on weekly death rates using machine
learning models. The primary objectives include:

- Preprocessing and cleaning data from MongoDB.
- Developing and evaluating various machine learning models such as Random Forest, KNN, and Logistic Regression.
- Addressing data imbalance using SMOTE.
- Visualizing model performance through ROC curves and feature importance plots.
- Comparing implementations between Python and R.

---

## **Team Members**

- **Cem Koyluoglu (Project Manager)**: Responsible for overseeing the project and managing tasks.
- **Lee Pettigrew**: Assisted with coding and technical implementation of models.
- **Likhita Kanikicherla**: Data visualization, video preparation, and reporting tasks.

---

## **Tasks Overview**

| **Task ID** | **Task Name**                             | **Description**                                                                                    | **Assignee(s)**                     | **Status** | **Priority** |
|-------------|-------------------------------------------|----------------------------------------------------------------------------------------------------|-------------------------------------|------------|--------------|
| **AI-001**  | Team Hierarchy Determination              | Define roles and responsibilities for the project team.                                            | Cem Koyluoglu                       | Done       | High         |
| **AI-002**  | Dataset Research                          | Analyze and select appropriate datasets for the project.                                           | Likhita Kanikicherla,Cem Koyluoglu, Lee Pettigrew                | Done       | High         |
| **AI-003**  | Setting Up MongoDB Dataset                | Load and organize datasets into MongoDB for preprocessing.                                         | Cem Koyluoglu                       | Done       | High         |
| **AI-004**  | Data Cleaning and Preparation             | Clean and preprocess the dataset from MongoDB.                                                     | Cem Koyluoglu, Lee Pettigrew        | Done       | High         |
| **AI-005**  | Data Visualization                        | Create initial data visualizations for exploratory analysis (e.g., age distribution, risk levels). | Likhita Kanikicherla                | Done       | Medium       |
| **AI-006**  | Model Development: Random Forest (Python) | Build and evaluate a Random Forest model in Python using Scikit-learn.                             | Cem Koyluoglu                       | Done       | High         |
| **AI-007**  | Model Development: Random Forest (R)      | Implement the Random Forest model in R and compare results with Python.                            | Lee Pettigrew                       | Done       | Medium       |
| **AI-008**  | Handling Class Imbalance                  | Use SMOTE to balance the dataset for better model performance.                                     | Cem Koyluoglu                       | Done       | High         |
| **AI-009**  | Feature Importance Analysis               | Analyze and visualize feature importance for the model.                                            | Likhita Kanikicherla                | Done       | Medium       |
| **AI-010**  | ROC Curve and AUC Evaluation              | Plot and evaluate the ROC curve and calculate AUC for model performance.                           | Cem Koyluoglu                       | Done       | High         |
| **AI-011**  | Model Development: KNN                    | Build a KNN model and compare its performance with the Random Forest model.                        | Cem Koyluoglu, Lee Pettigrew        | Done       | Medium       |
| **AI-012**  | Advanced Visualizations                   | Create advanced and interactive visualizations using Plotly or Dash.                               | Likhita Kanikicherla                | Done       | Medium       |
| **AI-013**  | AI Model Comparison                       | Document the comparison of Python and R implementations and explain the challenges faced in R.     | Cem Koyluoglu                       | Done       | High         |
| **AI-014**  | Explore Alternative AI Methods            | Use Logistic Regression and KNN as alternative models for comparison.                              | Cem Koyluoglu                       | Done       | Medium       |
| **AI-015**  | Analyze AI Application Challenges         | Document the challenges faced in data preprocessing and model development (e.g., class imbalance). | Cem Koyluoglu, Lee Pettigrew        | Done       | Medium       |
| **AI-016**  | Project Report                            | Compile a detailed report summarizing all analyses, visualizations, and model results.             | Likhita Kanikicherla                | Done       | High         |
| **AI-017**  | Creating Reports                          | Prepare intermediate and final reports for project documentation.                                  | Likhita Kanikicherla                | Done       | High         |
| **AI-018**  | Presentation and Submission               | Prepare the final project presentation and ensure successful submission.                           | Likhita Kanikicherla, Cem Koyluoglu | Done       | High         |
| **AI-019**  | README File Creation                      | Create and update the README file with project details, methodology, and results.                  | Cem Koyluoglu                       | Done       | High         |

---

## 📖 Project Overview

This project investigates the relationship between COVID-19 vaccination rates and mortality, focusing on both global
data and US-specific trends. Using advanced analytics and Python-based tools, the analysis aims to uncover key insights
and implications for public health policies. The study incorporates statistical analysis, machine learning, and dynamic
visualizations.

### Key Objectives:

- Analyze trends in death rates among unvaccinated, vaccinated without boosters, and bivalent booster groups in the US.
- Identify regional disparities in vaccine distribution and its impact on mortality globally.
- Examine correlations between vaccination rates and mortality using statistical and machine learning models.

## 🧰 Installation and Setup

### Prerequisites

- Python 3.8+
- MongoDB (local or cloud-based instance)
- Required libraries listed in `requirements.txt`

### Steps

1. **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/CodeGenesisTeam.git
    cd CodeGenesisTeam
    ```

2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Set up MongoDB:**
    - Add your MongoDB credentials in `.env`:
    ```plaintext
    MONGO_URI="your_mongo_connection_uri"
    DATABASE_NAME="codegenesis_db"
    ```

4. **Load raw data into MongoDB:**
    ```bash
    python scripts/data_to_mongo.py
    ```

5. **Run analyses using Jupyter Notebooks:**
    - `main.ipynb` for full data analysis.

## 📂 Project Structure

```
CodeGenesis-TEAM/
├── data/
│   ├── processed/           # Processed datasets
│   ├── raw/                 # Original datasets
│
├── img/                     # Images for README and report
├── notebooks/               # Jupyter Notebooks for analysis
│   ├── main.ipynb           # Main analysis notebook
│   ├── data_to_mongo.ipynb  # Data preprocessing and loading
│
├── scripts/                 # Python scripts for automation
├── reports/                 # Project reports and logs
│   ├── logs/                # Execution logs
│   ├── Final_Project.pdf    # Final project report
│
├── .env                     # MongoDB credentials
├── README.md                # Project documentation
└── requirements.txt         # Python dependencies
```

## 📊 Key Highlights

### 1️⃣ US Data Analysis

**Findings:**

- Bivalent booster recipients showed the lowest death rates.
- Death rates declined with vaccination campaigns.
- Significant differences identified through ANOVA and Tukey HSD tests.

### 2️⃣ Global Data Analysis

**Findings:**

- Strong negative correlation between vaccination rates and mortality.
- Regional disparities highlight unequal vaccine distribution.

### 3️⃣ Manufacturer Data Insights

- Pfizer and Moderna dominate high-income regions, while AstraZeneca focuses on low-to-middle-income countries.

## 🛠️ Key Features and Scripts

1. **Data Preprocessing:**
    - **Script:** `data_to_mongo.py`
    - Cleans and structures datasets for MongoDB storage.
2. **Statistical and Machine Learning Analysis:**
    - Linear regression and logistic regression models.
    - Random Forest with SMOTE for imbalanced data.
3. **Interactive Visualizations:**
    - Created using Matplotlib and Plotly for dynamic data insights.

## 📈 Visualizations

1. **Death Rate Trends (US):**
    - Time-series analysis comparing vaccinated and unvaccinated groups.

    <img src="img/img_2.png" alt="US Death Rate Trends" width="500"/>

2. **Global Vaccination Impact:**
    - Scatter plot of vaccination rates vs. mortality.

    <img src="img/img_3.png" alt="Global Vaccination Trends" width="500"/>

3. **Manufacturer Distribution:**
    - Stacked bar chart highlighting regional manufacturer contributions.

    <img src="img/img_2.png" alt="Manufacturer Distribution" width="500"/>

## 🎯 Insights

1. Vaccination reduces COVID-19 mortality, especially with booster doses.
2. Equitable vaccine distribution remains a global challenge.
3. Manufacturer strategies differ by region, impacting accessibility.


## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

For inquiries or feedback, please open an issue in the repository.
