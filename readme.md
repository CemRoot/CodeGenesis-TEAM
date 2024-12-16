![image](https://github.com/user-attachments/assets/168d6364-b487-46e7-a6d3-baa24183ff6d)



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
├── notebooks/                        # Jupyter Notebooks
│   ├── 00_data_collection.ipynb      # Collecting and downloading data
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
