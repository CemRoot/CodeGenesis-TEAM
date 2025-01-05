
# CodeGenesis TEAM: Comprehensive COVID-19 Data Analysis

## 📖 Project Overview

This project investigates the relationship between COVID-19 vaccination rates and mortality, focusing on both global data and US-specific trends. Using advanced analytics and Python-based tools, the analysis aims to uncover key insights and implications for public health policies. The study incorporates statistical analysis, machine learning, and dynamic visualizations.

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
    <img src="img/us_trends.png" alt="US Death Rate Trends" width="500"/>

2. **Global Vaccination Impact:**
    - Scatter plot of vaccination rates vs. mortality.
    <img src="img/global_trends.png" alt="Global Vaccination Trends" width="500"/>

3. **Manufacturer Distribution:**
    - Stacked bar chart highlighting regional manufacturer contributions.
    <img src="img/manufacturer_dist.png" alt="Manufacturer Distribution" width="500"/>

## 🎯 Insights
1. Vaccination reduces COVID-19 mortality, especially with booster doses.
2. Equitable vaccine distribution remains a global challenge.
3. Manufacturer strategies differ by region, impacting accessibility.

## 📜 License

This project is licensed under the MIT License. See the LICENSE file for details.

For inquiries or feedback, please open an issue in the repository.
