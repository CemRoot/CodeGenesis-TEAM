
# CodeGenesis TEAM: COVID-19 Data Analysis

## Project Description

This project is a comprehensive data analysis study that examines the impact of vaccination status on death rates during the COVID-19 pandemic and explores the distribution of global vaccine manufacturers. The analyses include:

1. **US Data**:
   - Examination of death rates among unvaccinated, fully vaccinated without booster, and fully vaccinated with bivalent booster groups.
   - Time series analysis, lag correlation, and statistical tests (ANOVA and Tukey HSD).

2. **Global Data**:
   - Distribution of final (cumulative) vaccine doses by manufacturers (Pfizer, Moderna, AstraZeneca, etc.) across countries.

3. **Combined Analysis**:
   - Cross-validation by merging US and global data.

## Installation and Usage

### Requirements
- Python 3.8+
- MongoDB (local or cloud)
- pip or conda

### Installation Steps
1. Clone the repository:

    ```sh
    git clone https://github.com/your-username/CodeGenesisTeam.git
    cd CodeGenesisTeam
    ```

2. Install dependencies:

    ```sh
    pip install -r requirements.txt
    ```

    or if using conda:

    ```sh
    conda install --file requirements.txt
    ```

3. Set up the `.env` file:
   Create a `.env` file in the project root directory and configure it as follows:

    ```sh
    MONGO_URI="mongodb+srv://username:password@cluster.mongodb.net"
    DATABASE_NAME="codegenesis_db"
    ```

4. Load data into MongoDB:
   Run the `data_to_mongo.py` script to load raw data into MongoDB:

    ```sh
    python data_to_mongo.py
    ```

## Project Structure

```
CodeGenesis-TEAM/
│
├── data/                              # Data directory
│   ├── raw/                           # Raw data
│   │   ├── covid-vaccine-doses-by-manufacturer.csv
│   │   ├── united-states-rates-of-covid-19-deaths-by-vaccination-status.csv
│   │   ├── readme_for_vaccination-status.md
│   └── processed/                     # Processed data
│       ├── cleaned_covid_vacc_manufacturer.csv
│       ├── cleaned_us_death_rates.csv
│       ├── cleaned_us_vaccination_rates.csv
│
│
├── notebooks/                         # Jupyter Notebooks
│   ├── data_to_mongo.py                   # Load data into MongoDB
│   ├── main.ipynb                     # Main analysis file
│   └── additional_notebooks.ipynb     # Additional analyses
│
├── reports/                           # Reports and logs
│   ├── logs/                          # Log files
│   └── final_report
│
├── .env                               # Environment variables
├── README.md                          # Project description file
└── requirements.txt                   # Python dependencies
```

## Usage
1. **Data Exploration and Cleaning**:
   - Open `main.ipynb` with Jupyter Notebook to explore and clean the data.

2. **Analysis and Visualization**:
   - The project includes statistical tests (ANOVA, Tukey HSD), time series analysis, and lag correlations.
   - Outputs are visualized graphically (Matplotlib, Seaborn).

3. **Reporting Results**:
   - Key findings are summarized in `reports/final_report.md`.

## Sample Outputs

### Time Series Analysis

### Lag Analysis

## License

This project is licensed under the MIT License. For more information, see the LICENSE file.

This `README.md` provides a comprehensive and accessible starting point for your project. Ensure that the file structure matches your actual directory layout.
