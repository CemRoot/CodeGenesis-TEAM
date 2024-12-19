
![Task Overview (Jira Table)](https://github.com/user-attachments/assets/79a41561-86eb-4166-8644-7d6545c0ed07)


```markdown
/CodeGenesisTeam/                     # Root project directory
│
├── data/                             # Data directory
│   ├── raw/                          # Raw (original) datasets
│   │   ├── covid-vaccinations-vs-covid-death-rate.csv
│   │   ├── covid-vaccine-doses-by-manufacturer.csv
│   │   ├── OECD_health_expenditure.csv
│   │   ├── united-states-rates-of-covid-19-deaths-by-vaccination-status.csv
│   │   ├── readme_for_vaccination-status.md
│   │   ├── readme_for_covid-vaccine-doses-by-manufacturer.md
│   │   └── readme_for_covid-vaccinations-vs-death-rate.md
│   │
│   ├── processed/                    # Processed data
│   │   ├── merged_dataset.csv        # Cleaned and merged dataset
│   │   └── README.md                 # Documentation for data processing steps
│
├── notebooks/                        # Jupyter Notebooks directory
│   ├── 01_data_exploration.ipynb     # Initial data exploration and analysis
│   ├── 02_data_to_mongo.ipynb        # Loading data into MongoDB
│   ├── 03_data_cleaning.ipynb        # Cleaning and preprocessing data
│   ├── 04_analysis.ipynb             # Data analysis and results
│   ├── 05_visualization.ipynb        # Visualizing results
│   └── 06_final_report.ipynb         # Final report and conclusions
│
├── reports/                          # Project reports and documentation
│   ├── project_report.pdf            # Final project report
│   └── project_journal.md            # Project journal (daily log)
│
├── .env                              # Environment variables (MongoDB credentials)
├── README.md                         # Main README file with project overview
└── requirements.txt                  # Python dependencies list
```


run the processing file and then streamlit run Scripts/dashboard.py to get the dashboard to show
