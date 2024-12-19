# Scripts/data_processing.py

import os
import sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend suitable for scripts
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import logging
from matplotlib.lines import Line2D  # For creating proxy artists in legends
import pycountry  # For country code mapping

# ----------------------------
# Configuration and Setup
# ----------------------------

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("covid_dashboard.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

# Set plot styles
sns.set(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Define paths relative to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
raw_data_path = os.path.join(project_root, 'data', 'raw')
processed_data_path = os.path.join(project_root, 'data', 'processed')

# Ensure processed data directory exists
os.makedirs(processed_data_path, exist_ok=True)

# ----------------------------
# Data Loading Functions
# ----------------------------

def load_data(raw_data_path):
    """
    Load CSV files into pandas DataFrames.

    Parameters:
        raw_data_path (str): Path to the directory containing raw CSV files.

    Returns:
        tuple: DataFrames for COVID deaths vs vaccinations, vaccine doses by manufacturer,
               OECD health expenditure, and US death rates by vaccination status.
    """
    try:
        logging.info("Loading datasets...")
        covid_death_vacc = pd.read_csv(os.path.join(raw_data_path, 'covid-vaccinations-vs-covid-death-rate.csv'))
        covid_doses_manu = pd.read_csv(os.path.join(raw_data_path, 'covid-vaccine-doses-by-manufacturer.csv'))
        oecd_health = pd.read_csv(os.path.join(raw_data_path, 'OECD_health_expenditure.csv'))
        us_death_rates = pd.read_csv(
            os.path.join(raw_data_path, 'united-states-rates-of-covid-19-deaths-by-vaccination-status.csv'))
        logging.info("Datasets loaded successfully.\n")
        logging.info(f"COVID Data Shape: {covid_death_vacc.shape}")
        logging.info(f"COVID Doses Data Shape: {covid_doses_manu.shape}")
        logging.info(f"OECD Health Data Shape: {oecd_health.shape}")
        logging.info(f"US Death Rates Data Shape: {us_death_rates.shape}")
        return covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates
    except FileNotFoundError as e:
        logging.error(f"Error loading data: {e}")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error loading data: {e}")
        sys.exit(1)

# ----------------------------
# Data Cleaning Functions
# ----------------------------

def clean_covid_death_vacc(df):
    """
    Clean the COVID-19 Death vs Vaccination dataset.

    Parameters:
        df (DataFrame): Raw COVID-19 deaths vs vaccinations data.

    Returns:
        DataFrame: Cleaned data.
    """
    logging.info("Cleaning covid-vaccinations-vs-covid-death-rate.csv...")
    df = df.copy()
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')
    # Drop rows where key columns are NaN
    df.dropna(subset=[
        "Daily new confirmed deaths due to COVID-19 per million people (rolling 7-day average, right-aligned)",
        "COVID-19 doses (cumulative, per hundred)"
    ], inplace=True)
    # Rename columns for clarity
    df.rename(columns={
        "year": "Year",
        "Daily new confirmed deaths due to COVID-19 per million people (rolling 7-day average, right-aligned)": "Daily_Deaths_per_Million",
        "COVID-19 doses (cumulative, per hundred)": "COVID_Doses_per_Hundred",
        "World regions according to OWID": "World_Region"
    }, inplace=True)
    logging.info("Cleaning completed.\n")
    logging.info(f"COVID Cleaned Data Shape: {df.shape}")
    return df

def clean_covid_doses_manu(df):
    """
    Clean the COVID-19 Vaccine Doses by Manufacturer dataset.

    Parameters:
        df (DataFrame): Raw vaccine doses by manufacturer data.

    Returns:
        DataFrame: Cleaned and melted data.
    """
    logging.info("Cleaning covid-vaccine-doses-by-manufacturer.csv...")
    df = df.copy()
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')
    df = df.fillna(0)  # Assuming missing values mean zero doses
    # Melt the dataframe to have one row per Entity, Code, Day, Manufacturer, Doses
    manufacturers = [col for col in df.columns if 'COVID-19 doses (cumulative) - Manufacturer' in col]
    df_melted = df.melt(id_vars=['Entity', 'Code', 'Day'], value_vars=manufacturers,
                        var_name='Manufacturer', value_name='COVID_Doses_Cumulative')
    # Remove the prefix from Manufacturer names using a raw string
    df_melted['Manufacturer'] = df_melted['Manufacturer'].str.replace(
        r'COVID-19 doses \(cumulative\) - Manufacturer ',
        '',
        regex=True
    )
    logging.info("Cleaning completed.\n")
    logging.info(f"COVID Doses Cleaned Data Shape: {df_melted.shape}")
    return df_melted

def clean_oecd_health(df):
    """
    Clean the OECD Health Expenditure dataset.

    Parameters:
        df (DataFrame): Raw OECD health expenditure data.

    Returns:
        DataFrame: Cleaned data focused on health expenditure as a percentage of GDP.
    """
    logging.info("Cleaning OECD_health_expenditure.csv...")
    df = df.copy()
    # Check for necessary columns
    required_columns = ['MEASURE', 'UNIT_MEASURE', 'REF_AREA', 'TIME_PERIOD', 'OBS_VALUE', 'Reference area']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        logging.error(f"Missing columns in OECD_health_expenditure.csv: {missing_columns}")
        sys.exit(1)

    # Log unique values before filtering
    unique_measures = df['MEASURE'].unique()
    unique_units = df['UNIT_MEASURE'].unique()
    logging.info(f"Unique MEASURE values before filtering: {unique_measures}")
    logging.info(f"Unique UNIT_MEASURE values before filtering: {unique_units}")

    # Update filtering criteria based on actual UNIT_MEASURE values
    # From the sample, 'PT_B1GQ' corresponds to 'Percentage of GDP'
    df_filtered = df[
        (df['MEASURE'] == 'EXP_HEALTH') &
        (df['UNIT_MEASURE'] == 'PT_B1GQ')
        ].copy()
    logging.info(f"DataFrame shape after filtering MEASURE and UNIT_MEASURE: {df_filtered.shape}")

    if df_filtered.empty:
        logging.error("Filtered OECD Health Expenditure DataFrame is empty. Check filtering criteria.")
        sys.exit(1)

    # Convert 'TIME_PERIOD' to datetime and extract 'Year'
    df_filtered['TIME_PERIOD'] = pd.to_datetime(df_filtered['TIME_PERIOD'], format='%Y', errors='coerce')
    df_filtered.dropna(subset=['TIME_PERIOD', 'OBS_VALUE'], inplace=True)
    df_filtered.rename(columns={
        'REF_AREA': 'Country_Code',
        'Reference area': 'Country',
        'TIME_PERIOD': 'Year',
        'OBS_VALUE': 'Health_Expenditure_Percentage_GDP'
    }, inplace=True)
    df_filtered['Year'] = df_filtered['Year'].dt.year  # Convert to integer

    # Log unique Country_Codes after cleaning
    unique_country_codes = df_filtered['Country_Code'].unique()
    logging.info(f"Unique Country_Codes after cleaning: {unique_country_codes}")
    logging.info("Cleaning completed.\n")
    logging.info(f"OECD Health Cleaned Data Shape: {df_filtered.shape}")
    return df_filtered

def clean_us_death_rates(df):
    """
    Clean the US Death Rates by Vaccination Status dataset.

    Parameters:
        df (DataFrame): Raw US death rates by vaccination status data.

    Returns:
        DataFrame: Cleaned data.
    """
    logging.info("Cleaning united-states-rates-of-covid-19-deaths-by-vaccination-status.csv...")
    df = df.copy()
    df['Day'] = pd.to_datetime(df['Day'], errors='coerce')
    # Rename columns for clarity
    df.rename(columns={
        "Death rate (weekly) of unvaccinated people - United States, by age": "Death_Rate_Unvaccinated",
        "Death rate (weekly) of fully vaccinated people (without bivalent booster) - United States, by age": "Death_Rate_Fully_Vaccinated",
        "Death rate (weekly) of fully vaccinated people (with bivalent booster) - United States, by age": "Death_Rate_Fully_Vaccinated_Bivalent"
    }, inplace=True)
    df.fillna(0, inplace=True)  # Assuming missing values mean zero deaths
    logging.info("Cleaning completed.\n")
    logging.info(f"US Death Rates Cleaned Data Shape: {df.shape}")
    return df

# ----------------------------
# Country Code Mapping Function
# ----------------------------

def get_country_code_mapping(covid_death_vacc):
    """
    Create a mapping between country names in covid_death_vacc dataset and their ISO alpha-3 country codes.
    Includes custom mappings for regions and groupings.

    Parameters:
        covid_death_vacc (DataFrame): Cleaned COVID deaths vs vaccinations data.

    Returns:
        dict: Mapping from Entity to Country_Code.
    """
    mapping = {}
    # Custom mappings for regions and groupings
    custom_mappings = {
        "Africa": "AFR",  # Custom code
        "Asia": "ASIA",
        "Europe": "EUR",
        "European Union (27)": "EU27",
        "North America": "NAM",
        "Oceania": "OCE",
        "South America": "SAM",
        "World": "WORLD",
        "Low-income countries": "LOW",
        "Lower-middle-income countries": "LMIC",
        "Upper-middle-income countries": "UMIC",
        "High-income countries": "HIGH",
        "Bonaire Sint Eustatius and Saba": "BES",
        "Cote d'Ivoire": "CIV",
        "Cabo Verde": "CPV",
        "Democratic Republic of Congo": "COD",
        "East Timor": "TLS",
        "Curacao": "CUW",
        "Falkland Islands": "FLK",
        "Kosovo": "XKX",
        "Palestine": "PSE",
        "Russia": "RUS",
        "Saint Helena": "SHN",
        "Turkey": "TUR",
        "Brunei Darussalam": "BRN",  # Alternative name
        "Brunei": "BRN",  # Original mapping
        "Cape Verde": "CPV",
        "Cabo Verde": "CPV",  # Alternative name
        # Add more as needed
    }

    unmapped_entities = []
    for entity in covid_death_vacc['Entity'].unique():
        if entity in custom_mappings:
            mapping[entity] = custom_mappings[entity]
        else:
            try:
                # Attempt to find the country in pycountry
                country = pycountry.countries.lookup(entity)
                mapping[entity] = country.alpha_3
            except LookupError:
                # If not found, log and collect unmapped entities
                logging.warning(f"Could not find country code for Entity: {entity}")
                unmapped_entities.append(entity)
                mapping[entity] = np.nan
    if unmapped_entities:
        logging.info(f"Total Unmapped Entities: {len(unmapped_entities)}")
        logging.info(f"Unmapped Entities: {unmapped_entities}")
    return mapping

# ----------------------------
# Data Merging Function
# ----------------------------

def merge_datasets(covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates):
    """
    Merge all cleaned datasets into a single DataFrame, focusing on individual countries.

    Parameters:
        covid_death_vacc (DataFrame): Cleaned COVID deaths vs vaccinations data.
        covid_doses_manu (DataFrame): Cleaned vaccine doses by manufacturer data.
        oecd_health (DataFrame): Cleaned OECD health expenditure data.
        us_death_rates (DataFrame): Cleaned US death rates by vaccination status data.

    Returns:
        DataFrame: Merged dataset containing only individual countries.
    """
    logging.info("Merging datasets...")

    # Create country code mapping
    country_code_mapping = get_country_code_mapping(covid_death_vacc)
    covid_death_vacc['Country_Code'] = covid_death_vacc['Entity'].map(country_code_mapping)

    # Filter to include only individual countries (those with 3-letter ISO codes)
    covid_death_vacc_countries = covid_death_vacc[
        covid_death_vacc['Country_Code'].apply(lambda x: isinstance(x, str) and len(x) == 3)
    ].copy()

    # Log unique Country_Codes
    unique_covid_codes = set(covid_death_vacc_countries['Country_Code'].dropna().unique())
    unique_oecd_codes = set(oecd_health['Country_Code'].dropna().unique())
    common_codes = unique_covid_codes.intersection(unique_oecd_codes)

    logging.info(f"Unique Country_Codes in COVID Data: {len(unique_covid_codes)}")
    logging.info(f"Unique Country_Codes in OECD Data: {len(unique_oecd_codes)}")
    logging.info(f"Number of Common Country_Codes: {len(common_codes)}")

    if not common_codes:
        logging.error("No common Country_Codes found between COVID Data and OECD Health Data.")
        sys.exit(1)

    # Log Year ranges
    covid_year_min = covid_death_vacc_countries['Year'].min()
    covid_year_max = covid_death_vacc_countries['Year'].max()
    oecd_year_min = oecd_health['Year'].min()
    oecd_year_max = oecd_health['Year'].max()

    logging.info(f"COVID Data Year Range: {covid_year_min} - {covid_year_max}")
    logging.info(f"OECD Health Data Year Range: {oecd_year_min} - {oecd_year_max}")

    # Merge COVID Deaths with Vaccinations
    merged = pd.merge(
        covid_death_vacc_countries,
        covid_doses_manu,
        on=['Entity', 'Code', 'Day'],
        how='left',
        suffixes=('_death_vacc', '_doses_manu')
    )
    logging.info(f"After merging COVID and Doses Data: {merged.shape}")

    # Merge with OECD Health Expenditure on 'Country_Code' and 'Year' using inner join
    merged = pd.merge(
        merged, oecd_health,
        on=['Country_Code', 'Year'],
        how='inner'  # Changed to 'inner' to retain only matching records
    )
    logging.info(f"After merging with OECD Health Data: {merged.shape}")

    # Merge with US Death Rates on 'Year'
    us_death = us_death_rates.copy()
    us_death['Year'] = us_death['Day'].dt.year
    us_death = us_death.groupby('Year').agg({
        'Death_Rate_Unvaccinated': 'mean',
        'Death_Rate_Fully_Vaccinated': 'mean',
        'Death_Rate_Fully_Vaccinated_Bivalent': 'mean'
    }).reset_index()
    merged = pd.merge(merged, us_death, on='Year', how='left')
    logging.info(f"After merging with US Death Rates: {merged.shape}")

    # Handle missing Health Expenditure
    health_exp_nan = merged['Health_Expenditure_Percentage_GDP'].isna().sum()
    if health_exp_nan > 0:
        # Fill with mean or median if available
        mean_health_exp = merged['Health_Expenditure_Percentage_GDP'].mean()
        if not np.isnan(mean_health_exp):
            merged['Health_Expenditure_Percentage_GDP'] = merged['Health_Expenditure_Percentage_GDP'].fillna(
                mean_health_exp)
            logging.info(
                f"Filled {health_exp_nan} NaN values in 'Health_Expenditure_Percentage_GDP' with mean value: {mean_health_exp:.2f}"
            )
        else:
            median_health_exp = merged['Health_Expenditure_Percentage_GDP'].median()
            if not np.isnan(median_health_exp):
                merged['Health_Expenditure_Percentage_GDP'] = merged['Health_Expenditure_Percentage_GDP'].fillna(
                    median_health_exp)
                logging.info(
                    f"Filled {health_exp_nan} NaN values in 'Health_Expenditure_Percentage_GDP' with median value: {median_health_exp:.2f}"
                )
            else:
                # Drop rows if both mean and median are NaN
                merged = merged.dropna(subset=['Health_Expenditure_Percentage_GDP'])
                logging.warning(
                    "Median health expenditure is also NaN. Dropping rows with missing health expenditure data."
                )

    # Save the merged DataFrame to a CSV file for dashboard use
    merged_data_path = os.path.join(processed_data_path, 'merged_data.csv')
    merged.to_csv(merged_data_path, index=False)
    logging.info(f"Merged data saved to {merged_data_path}")

    logging.info("Merging completed.\n")
    logging.info(f"Merged DataFrame shape: {merged.shape}")
    return merged

# ----------------------------
# Data Analysis and Visualization
# ----------------------------

def perform_analysis(merged_df, processed_data_path):
    """
    Perform exploratory data analysis and generate visualizations.

    Parameters:
        merged_df (DataFrame): The merged dataset.
        processed_data_path (str): Path to save the generated visualizations.
    """
    logging.info("Starting data analysis...\n")

    if merged_df.empty:
        logging.error("Merged DataFrame is empty. Aborting analysis.")
        return

    # Check for NaN or infinite values in key columns
    key_columns = ['COVID_Doses_per_Hundred', 'Daily_Deaths_per_Million', 'Health_Expenditure_Percentage_GDP']
    for col in key_columns:
        if merged_df[col].isnull().any():
            logging.warning(f"Column '{col}' contains NaN values.")
        if np.isinf(merged_df[col]).any():
            logging.warning(f"Column '{col}' contains infinite values.")

    # 1. COVID-19 Doses vs Daily Deaths per Million
    try:
        logging.info("Generating plot: COVID-19 Doses vs Daily Deaths per Million")
        plt.figure(figsize=(10, 6))
        scatter = sns.scatterplot(
            data=merged_df,
            x='COVID_Doses_per_Hundred',
            y='Daily_Deaths_per_Million',
            hue='World_Region',
            alpha=0.6,
            palette='viridis',
            edgecolor=None,
            legend='brief'
        )
        # Regression line
        reg = sns.regplot(
            data=merged_df,
            x='COVID_Doses_per_Hundred',
            y='Daily_Deaths_per_Million',
            scatter=False,
            color='red'
        )
        plt.title('COVID-19 Doses vs Daily Deaths per Million')
        plt.xlabel('COVID-19 Doses (per Hundred)')
        plt.ylabel('Daily Deaths per Million')

        # Create proxy artist for regression line
        proxy = Line2D([0], [0], color='red', label='Regression Line')

        # Adjust legend to include regression line
        handles, labels = scatter.get_legend_handles_labels()
        if 'World_Region' in labels:
            world_region_index = labels.index('World_Region')
            # Remove the default legend entry for 'World_Region' to prevent duplication
            handles.pop(world_region_index)
            labels.pop(world_region_index)
        handles.append(proxy)
        labels.append('Regression Line')
        plt.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plot1_path = os.path.join(processed_data_path, 'covid_doses_vs_deaths.png')
        plt.savefig(plot1_path)
        plt.close()
        logging.info(f"Saved plot: {plot1_path}")
    except Exception as e:
        logging.error(f"Error generating plot1: {e}")

    # 2. COVID-19 Cumulative Doses by Top 5 Manufacturers Over Time
    try:
        logging.info("Generating plot: COVID-19 Cumulative Doses by Top 5 Manufacturers Over Time")
        plt.figure(figsize=(14, 7))

        # Aggregate data by Month and Manufacturer
        merged_df['Month'] = merged_df['Day'].dt.to_period('M').dt.to_timestamp()
        monthly_data = merged_df.groupby(['Month', 'Manufacturer'])['COVID_Doses_Cumulative'].max().reset_index()

        # Identify top 5 manufacturers by total doses
        top_manufacturers = merged_df.groupby('Manufacturer')['COVID_Doses_Cumulative'].sum().sort_values(
            ascending=False).head(5).index.tolist()

        # Filter to include only top manufacturers
        monthly_data_top = monthly_data[monthly_data['Manufacturer'].isin(top_manufacturers)].copy()

        if monthly_data_top.empty:
            logging.warning("No data available for the top 5 manufacturers.")
        else:
            sns.lineplot(
                data=monthly_data_top,
                x='Month',
                y='COVID_Doses_Cumulative',
                hue='Manufacturer',
                palette='tab10',
                linewidth=2,
                marker='o'
            )
            plt.title('COVID-19 Cumulative Doses by Top 5 Manufacturers Over Time')
            plt.xlabel('Month')
            plt.ylabel('Cumulative Doses')

            plt.legend(title='Manufacturer', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, title_fontsize=14)
            plt.tight_layout()
            plot2_path = os.path.join(processed_data_path, 'doses_by_manufacturer_over_time.png')
            plt.savefig(plot2_path)
            plt.close()
            logging.info(f"Saved plot: {plot2_path}")
    except Exception as e:
        logging.error(f"Error generating plot2: {e}")

    # 3. Health Expenditure (% of GDP) vs Daily COVID-19 Deaths per Million
    try:
        logging.info("Generating plot: Health Expenditure (% of GDP) vs Daily COVID-19 Deaths per Million")

        # Verify that all NaNs are handled
        nan_count = merged_df['Health_Expenditure_Percentage_GDP'].isna().sum()
        if nan_count > 0:
            logging.warning(f"Still {nan_count} NaN values in 'Health_Expenditure_Percentage_GDP' after filling.")

        plt.figure(figsize=(10, 6))

        # Scatter plot
        scatter = sns.scatterplot(
            data=merged_df,
            x='Health_Expenditure_Percentage_GDP',
            y='Daily_Deaths_per_Million',
            hue='World_Region',
            palette='viridis',
            alpha=0.6,
            edgecolor=None,
            legend='brief'
        )

        # Regression line
        reg = sns.regplot(
            data=merged_df,
            x='Health_Expenditure_Percentage_GDP',
            y='Daily_Deaths_per_Million',
            scatter=False,
            color='red'
        )

        plt.title('Health Expenditure (% of GDP) vs Daily COVID-19 Deaths per Million')
        plt.xlabel('Health Expenditure (% of GDP)')
        plt.ylabel('Daily Deaths per Million')

        # Create proxy artist for regression line
        proxy = Line2D([0], [0], color='red', label='Regression Line')

        # Adjust legend to include regression line
        handles, labels = scatter.get_legend_handles_labels()
        if 'World_Region' in labels:
            world_region_index = labels.index('World_Region')
            # Remove the default legend entry for 'World_Region' to prevent duplication
            handles.pop(world_region_index)
            labels.pop(world_region_index)
        handles.append(proxy)
        labels.append('Regression Line')
        plt.legend(handles, labels, bbox_to_anchor=(1.05, 1), loc='upper left')

        plt.tight_layout()
        plot3_path = os.path.join(processed_data_path, 'health_expenditure_vs_deaths.png')
        plt.savefig(plot3_path)
        plt.close()
        logging.info(f"Saved plot: {plot3_path}")
    except Exception as e:
        logging.error(f"Error generating plot3: {e}")

    # 4. Interactive Visualization: Weekly Death Rates in the US by Vaccination Status
    try:
        logging.info("Generating interactive plot: Weekly Death Rates in the US by Vaccination Status")
        fig = px.line(
            merged_df,
            x='Year',
            y=['Death_Rate_Unvaccinated', 'Death_Rate_Fully_Vaccinated', 'Death_Rate_Fully_Vaccinated_Bivalent'],
            labels={'value': 'Death Rate', 'variable': 'Vaccination Status'},
            title='Weekly Death Rates in the US by Vaccination Status',
            template='plotly_dark'
        )
        interactive_plot_path = os.path.join(processed_data_path, 'us_death_rates_interactive.html')
        fig.write_html(interactive_plot_path)
        logging.info(f"Saved interactive plot: {interactive_plot_path}")
    except Exception as e:
        logging.error(f"Error generating interactive plot: {e}")

    # 5. Improved Correlation Heatmap with More Variables
    try:
        logging.info("Generating plot: Improved Correlation Heatmap")
        plt.figure(figsize=(16, 12))

        # Select a broader range of numerical columns for correlation
        correlation_cols = [
            'Daily_Deaths_per_Million',
            'COVID_Doses_per_Hundred',
            'Health_Expenditure_Percentage_GDP',
            'COVID_Doses_Cumulative',
            'Year'
        ]

        # Ensure selected columns exist
        existing_corr_cols = [col for col in correlation_cols if col in merged_df.columns]

        if len(existing_corr_cols) < 2:
            logging.warning("Not enough columns for correlation heatmap.")
        else:
            corr = merged_df[existing_corr_cols].corr()

            # Generate a mask for the upper triangle
            mask = np.triu(np.ones_like(corr, dtype=bool))

            # Define a custom diverging palette
            cmap = sns.diverging_palette(220, 10, as_cmap=True)

            sns.heatmap(
                corr,
                mask=mask,
                annot=True,
                fmt=".2f",
                cmap=cmap,
                linewidths=.5,
                annot_kws={"size": 14},
                cbar_kws={"shrink": .5},
                square=True
            )

            plt.title('Correlation Heatmap', fontsize=20, pad=20)
            plt.xticks(rotation=45, ha='right', fontsize=14)
            plt.yticks(rotation=0, fontsize=14)

            plt.tight_layout()
            plot5_path = os.path.join(processed_data_path, 'correlation_heatmap.png')
            plt.savefig(plot5_path)
            plt.close()
            logging.info(f"Saved plot: {plot5_path}")
    except Exception as e:
        logging.error(f"Error generating plot5: {e}")

    # 6. Time Series of COVID Deaths per Million by Region
    try:
        logging.info("Generating plot: Time Series of COVID Deaths per Million by Region")

        plt.figure(figsize=(18, 10))

        # Aggregate data by date and region to smooth out daily fluctuations
        time_series = merged_df.groupby(['Day', 'World_Region'])['Daily_Deaths_per_Million'].mean().reset_index()

        sns.lineplot(
            data=time_series,
            x='Day',
            y='Daily_Deaths_per_Million',
            hue='World_Region',
            palette='tab10',
            linewidth=2,
            marker='o',
            errorbar=None  # Updated from ci=None to suppress future warning
        )

        plt.title('Time Series of Daily COVID-19 Deaths per Million by World Region', fontsize=20)
        plt.xlabel('Date', fontsize=16)
        plt.ylabel('Daily Deaths per Million', fontsize=16)

        plt.legend(title='World Region', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12, title_fontsize=14)
        plt.tight_layout()
        plot6_path = os.path.join(processed_data_path, 'time_series_deaths_by_region.png')
        plt.savefig(plot6_path)
        plt.close()
        logging.info(f"Saved plot: {plot6_path}")
    except Exception as e:
        logging.error(f"Error generating plot6: {e}")

    # 7. Distribution of COVID Doses per Hundred
    try:
        logging.info("Generating plot: Distribution of COVID-19 Doses per Hundred")

        plt.figure(figsize=(12, 8))

        sns.histplot(
            merged_df['COVID_Doses_per_Hundred'],
            bins=100,
            kde=True,
            color='teal',
            edgecolor='black'
        )

        plt.title('Distribution of COVID-19 Doses per Hundred', fontsize=20)
        plt.xlabel('COVID-19 Doses (per Hundred)', fontsize=16)
        plt.ylabel('Frequency', fontsize=16)

        plt.tight_layout()
        plot7_path = os.path.join(processed_data_path, 'distribution_covid_doses.png')
        plt.savefig(plot7_path)
        plt.close()
        logging.info(f"Saved plot: {plot7_path}")
    except Exception as e:
        logging.error(f"Error generating plot7: {e}")

    logging.info("Data analysis and visualizations completed.\n")

# ----------------------------
# Country Code Mapping Function (Cached)
# ----------------------------

def create_country_code_mapping(covid_death_vacc):
    return get_country_code_mapping(covid_death_vacc)

# ----------------------------
# Data Merging Function (Cached)
# ----------------------------

def get_merged_data(covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates):
    return merge_datasets(covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates)

# ----------------------------
# Load and Process Data
# ----------------------------

def load_and_process_data():
    """
    Load, clean, merge, and analyze data.

    Returns:
        DataFrame: Merged and processed dataset.
    """
    # Load data
    covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates = load_data(raw_data_path)

    # Clean data
    covid_death_vacc = clean_covid_death_vacc(covid_death_vacc)
    covid_doses_manu = clean_covid_doses_manu(covid_doses_manu)
    oecd_health = clean_oecd_health(oecd_health)
    us_death_rates = clean_us_death_rates(us_death_rates)

    # Merge datasets
    merged_df = merge_datasets(covid_death_vacc, covid_doses_manu, oecd_health, us_death_rates)

    # Perform analysis and generate visualizations
    perform_analysis(merged_df, processed_data_path)

    return merged_df

# ----------------------------
# Main Execution
# ----------------------------

def main():
    """
    Main function to orchestrate data loading, cleaning, merging, analysis, and generating visualizations.
    """
    logging.info("Starting data processing script.")
    merged_df = load_and_process_data()
    logging.info("Data processing completed successfully.\n")

if __name__ == "__main__":
    main()
