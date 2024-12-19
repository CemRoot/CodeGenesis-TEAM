# dashboard.py

import os
import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from datetime import datetime

# ----------------------------
# Streamlit Configuration
# ----------------------------

st.set_page_config(
    page_title="🌐 COVID-19 Data Analysis Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Define Paths
# ----------------------------

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
processed_data_path = os.path.join(project_root, 'data', 'processed')

merged_data_path = os.path.join(processed_data_path, 'merged_data.csv')

# ----------------------------
# Setup Logging
# ----------------------------

log_file_path = os.path.join(project_root, 'covid_dashboard.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler()
    ]
)


# ----------------------------
# Load Data
# ----------------------------

@st.cache_data
def load_data(path):
    """
    Load merged COVID-19 data from CSV with dynamic date parsing.
    """
    try:
        # First, read the CSV without parsing dates to inspect columns
        df = pd.read_csv(path, low_memory=False)
        original_columns = df.columns.tolist()
        logging.info(f"Original Data Columns: {original_columns}")

        # Define potential date columns you expect
        potential_date_cols = ['day', 'date', 'Day', 'Date', 'DATE']

        # Find which of the potential date columns exist in the DataFrame
        existing_date_cols = [col for col in potential_date_cols if col in df.columns]

        if not existing_date_cols:
            raise KeyError(f"No date column found among {potential_date_cols}. Please verify your CSV file.")

        # Proceed to read the CSV again with the correct date parsing
        df = pd.read_csv(path, parse_dates=existing_date_cols, low_memory=False)

        # Clean and standardize column names
        df.rename(columns=lambda x: x.strip().replace(' ', '_').replace('\n', '').replace('\r', '').lower(),
                  inplace=True)

        logging.info(f"Loaded data with shape: {df.shape}")
        logging.info(f"Data columns after cleaning: {df.columns.tolist()}")
        return df
    except FileNotFoundError:
        st.error(f"Data file not found at {path}. Please run the data processing script first.")
        logging.error(f"Data file not found at {path}.")
        st.stop()
    except KeyError as ke:
        st.error(f"Key Error: {ke}")
        logging.error(f"Key Error: {ke}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        logging.error(f"Error loading data: {e}")
        st.stop()


# Load the merged DataFrame
merged_df = load_data(merged_data_path)


# ----------------------------
# Data Cleaning and Preparation
# ----------------------------

def clean_data(df):
    """
    Perform additional data cleaning steps if necessary.
    """
    # Handle missing values
    required_columns = ['country_code', 'daily_deaths_per_million', 'covid_doses_per_hundred',
                        'health_expenditure_percentage_gdp']
    df = df.dropna(subset=required_columns)

    # Convert 'time_period' to datetime if not already
    if 'time_period' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['time_period']):
        df['time_period'] = pd.to_datetime(df['time_period'])

    # Optional: Check for negative or unrealistic values and handle them
    df = df[(df['covid_doses_per_hundred'] >= 0) & (df['daily_deaths_per_million'] >= 0)]

    return df


merged_df = clean_data(merged_df)


# ----------------------------
# Plotting Functions
# ----------------------------

@st.cache_data
def get_line_plot(data, x_col, y_col, color_col, title, labels, facet_col=None):
    """
    Generate an interactive line plot with optional faceting.
    """
    try:
        if facet_col:
            fig = px.line(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                facet_col=facet_col,
                title=title,
                labels=labels,
                markers=True,
                template='plotly_dark'
            )
        else:
            fig = px.line(
                data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=title,
                labels=labels,
                markers=True,
                template='plotly_dark'
            )
        fig.update_layout(legend_title_text=color_col.replace('_', ' ').title())
        fig.update_traces(mode='lines+markers')
        return fig
    except Exception as e:
        logging.error(f"Error generating line plot: {e}")
        st.error("An error occurred while generating the line plot.")
        return None


@st.cache_data
def get_facet_scatter_plot(data, x_col, y_col, color_col, facet_col, title, labels):
    """
    Generate a faceted scatter plot.
    """
    try:
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            color=color_col,
            facet_col=facet_col,
            title=title,
            labels=labels,
            trendline='ols',
            template='plotly_dark',
            size_max=15,
            opacity=0.7
        )
        fig.update_layout(legend_title_text=color_col.replace('_', ' ').title())
        return fig
    except Exception as e:
        logging.error(f"Error generating faceted scatter plot: {e}")
        st.error("An error occurred while generating the faceted scatter plot.")
        return None


@st.cache_data
def get_bar_chart(data, x_col, y_col, title, labels):
    """
    Generate a bar chart.
    """
    try:
        fig = px.bar(
            data,
            x=x_col,
            y=y_col,
            title=title,
            labels=labels,
            template='plotly_dark',
            color=y_col,
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False)
        return fig
    except Exception as e:
        logging.error(f"Error generating bar chart: {e}")
        st.error("An error occurred while generating the bar chart.")
        return None


@st.cache_data
def get_histogram(data, x_col, title, labels):
    """
    Generate a histogram with density overlay.
    """
    try:
        fig = px.histogram(
            data,
            x=x_col,
            nbins=100,
            marginal="box",
            title=title,
            labels={'covid_doses_per_hundred': 'COVID-19 Doses (per Hundred)', 'count': 'Frequency'},
            template='plotly_dark',
            opacity=0.7,
            color_discrete_sequence=['#636EFA']
        )
        return fig
    except Exception as e:
        logging.error(f"Error generating histogram: {e}")
        st.error("An error occurred while generating the histogram.")
        return None


@st.cache_data
def get_correlation_heatmap(df):
    """
    Generate and save a correlation heatmap.
    """
    try:
        import seaborn as sns
        import matplotlib.pyplot as plt

        correlation = df[
            ['covid_doses_per_hundred', 'daily_deaths_per_million', 'health_expenditure_percentage_gdp']].corr()

        plt.figure(figsize=(8, 6))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt=".2f")
        plt.title('Correlation Heatmap of Key Metrics')
        heatmap_path = os.path.join(processed_data_path, 'correlation_heatmap.png')
        plt.savefig(heatmap_path, bbox_inches='tight')
        plt.close()
        return heatmap_path
    except Exception as e:
        logging.error(f"Error generating correlation heatmap: {e}")
        return None


# ----------------------------
# Sidebar Configuration
# ----------------------------

st.sidebar.title("📊 Navigation")
tabs = st.sidebar.radio("Go to", [
    "🏠 Home",
    "📊 COVID Doses Analysis",
    "🏭 Manufacturer Insights",
    "💰 Health Expenditure",
    "🇺🇸 US Vaccination Status",
    "📈 Correlation Analysis",
    "🌍 Regional Insights",
    "📉 Distribution Analysis",
    "🗃️ Data Inspection",
    "📥 Download Visualizations"
])

# ----------------------------
# Home Tab
# ----------------------------

if tabs == "🏠 Home":
    st.title("🌐 COVID-19 Data Analysis Dashboard")
    st.markdown("""
    Welcome to the COVID-19 Data Analysis Dashboard. This platform provides comprehensive insights into COVID-19 trends, vaccination rates, health expenditures, and more across various regions and demographics. Navigate through the sidebar to explore detailed analyses and interactive visualizations.
    """)

    # Display key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        # Median of the latest daily deaths per million
        latest_deaths = merged_df.sort_values('day').groupby('country_code')['daily_deaths_per_million'].last().median()
        st.metric(label="💀 Median COVID-19 Deaths per Million", value=f"{latest_deaths:,.2f}")
    with col2:
        # Median of the latest COVID doses per hundred
        latest_doses = merged_df.sort_values('day').groupby('country_code')['covid_doses_per_hundred'].last().median()
        st.metric(label="💉 Median COVID-19 Doses per Hundred", value=f"{latest_doses:,.2f}")
    with col3:
        avg_health_expenditure = merged_df['health_expenditure_percentage_gdp'].mean()
        st.metric(label="💰 Average Health Expenditure (% of GDP)", value=f"{avg_health_expenditure:.2f}%")

    # Display Summary Statistics for Verification
    st.markdown("### 📊 Summary Statistics")
    summary_deaths = merged_df['daily_deaths_per_million'].describe()
    summary_doses = merged_df['covid_doses_per_hundred'].describe()
    st.write("**Daily Deaths per Million**")
    st.table(summary_deaths)
    st.write("**COVID-19 Doses per Hundred**")
    st.table(summary_doses)

    # Key Insights
    st.markdown("""
    ## 🔍 Key Insights
    - **Vaccination Rates**: Analysis of COVID-19 doses administered globally.
    - **Death Rates**: Trends in daily COVID-19 deaths per million across regions.
    - **Health Expenditure**: Correlation between health spending and COVID-19 outcomes.
    - **Manufacturer Contributions**: Insights into top vaccine manufacturers.
    - **US Vaccination Impact**: Understanding the effect of vaccination status on death rates.
    """)

    # Interactive Map
    st.subheader("🌍 Global COVID-19 Doses per Hundred")
    # Aggregate data for map
    if 'country_name' in merged_df.columns:
        # If 'country_name' exists, use it
        map_data = merged_df.sort_values('day').groupby(['country_code', 'country_name'])[
            'covid_doses_per_hundred'].last().reset_index()
        fig_map = px.choropleth(
            map_data,
            locations="country_code",
            color="covid_doses_per_hundred",
            hover_name="country_name",
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Global COVID-19 Doses per Hundred',
            labels={'covid_doses_per_hundred': 'Doses per Hundred'}
        )
    elif 'country' in merged_df.columns:
        # Use 'country' if 'country_name' does not exist
        map_data = merged_df.sort_values('day').groupby(['country_code', 'country'])[
            'covid_doses_per_hundred'].last().reset_index()
        fig_map = px.choropleth(
            map_data,
            locations="country_code",
            color="covid_doses_per_hundred",
            hover_name="country",
            color_continuous_scale=px.colors.sequential.Viridis,
            title='Global COVID-19 Doses per Hundred',
            labels={'covid_doses_per_hundred': 'Doses per Hundred'}
        )
    else:
        st.warning("No appropriate country name column found for the map.")
        fig_map = None

    if fig_map:
        fig_map.update_layout(template='plotly_dark')
        st.plotly_chart(fig_map, use_container_width=True)

    # Additional Feature: Latest Updates
    st.markdown("### 📅 Latest Update")
    latest_date = merged_df['day'].max()
    st.write(f"The data is updated up to **{latest_date.strftime('%B %d, %Y')}**.")

    # Display Data Overview
    st.markdown("### 🔍 Data Overview")

    # Summary Statistics
    st.markdown("**Summary Statistics for Key Metrics:**")
    st.write(merged_df[['daily_deaths_per_million', 'covid_doses_per_hundred']].describe())

    # Sample Data
    if 'country' in merged_df.columns:
        st.markdown("**Sample Data Points:**")
        st.dataframe(merged_df[['country', 'day', 'daily_deaths_per_million', 'covid_doses_per_hundred']].head(20))
    else:
        st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# COVID Doses Analysis Tab
# ----------------------------

elif tabs == "📊 COVID Doses Analysis":
    st.title("💉 COVID-19 Doses vs Daily Deaths per Million")

    # Interactive Filters
    st.sidebar.header("📂 Filters")
    regions = ["All"] + sorted(merged_df['world_region'].dropna().unique().tolist())
    selected_region = st.sidebar.selectbox("Select World Region", regions)

    # Additional Filters: Sampling and Aggregation
    st.sidebar.subheader("⚙️ Performance Settings")
    sample_data = st.sidebar.checkbox("🔍 Enable Data Sampling for Performance", value=True)
    sample_size = st.sidebar.slider("Select Sample Size", min_value=1000, max_value=50000, step=1000, value=10000)
    aggregation_level = st.sidebar.selectbox("📅 Select Aggregation Level", ["None", "Monthly", "Quarterly", "Yearly"])

    # Filter Data Based on Selection
    if selected_region != "All":
        filtered_data = merged_df[merged_df['world_region'] == selected_region].copy()
    else:
        filtered_data = merged_df.copy()

    # Apply Aggregation
    if aggregation_level == "Monthly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('M').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'covid_doses_per_hundred': 'median',
            'daily_deaths_per_million': 'median'
        }).reset_index()
    elif aggregation_level == "Quarterly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Q').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'covid_doses_per_hundred': 'median',
            'daily_deaths_per_million': 'median'
        }).reset_index()
    elif aggregation_level == "Yearly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Y').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'covid_doses_per_hundred': 'median',
            'daily_deaths_per_million': 'median'
        }).reset_index()
    else:
        aggregated_data = filtered_data.copy()

    # Apply Sampling
    if sample_data and len(aggregated_data) > sample_size:
        aggregated_data = aggregated_data.sample(n=sample_size, random_state=42)
        st.info(f"Data has been sampled to {sample_size} records for improved performance.")

    # Check if data is empty after filtering
    if aggregated_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Plot Generation with Enhanced Line Plot
        fig = get_line_plot(
            data=aggregated_data,
            x_col='time_period',
            y_col='daily_deaths_per_million',
            color_col='world_region',
            title='COVID-19 Doses vs Daily Deaths per Million Over Time',
            labels={
                'time_period': 'Time Period',
                'daily_deaths_per_million': 'Daily Deaths per Million',
                'world_region': 'World Region'
            },
            facet_col=None  # Set to 'world_region' if you want to facet by region
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Additional Feature: Download Filtered Data
    st.markdown("### 📥 Download Filtered Data")
    csv = aggregated_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='covid_doses_vs_deaths_filtered.csv',
        mime='text/csv',
    )

    # Display Summary Statistics
    st.markdown("### 🔍 Data Overview")

    # Summary Statistics
    st.markdown("**Summary Statistics for Selected Data:**")
    st.write(aggregated_data[['daily_deaths_per_million', 'covid_doses_per_hundred']].describe())

    # Sample Data
    if 'country' in merged_df.columns:
        st.markdown("**Sample Data Points:**")
        st.dataframe(aggregated_data[
                         ['time_period', 'world_region', 'daily_deaths_per_million', 'covid_doses_per_hundred']].head(
            20))
    else:
        st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Manufacturer Insights Tab
# ----------------------------

elif tabs == "🏭 Manufacturer Insights":
    st.title("🏭 COVID-19 Vaccine Doses by Manufacturer Over Time")

    # Interactive Manufacturer Selection
    manufacturers = ["All"] + sorted(merged_df['manufacturer'].dropna().unique().tolist())
    selected_manufacturer = st.selectbox("Select Manufacturer", manufacturers)

    # Additional Filters: Sampling and Aggregation
    st.sidebar.subheader("⚙️ Performance Settings")
    sample_data = st.sidebar.checkbox("🔍 Enable Data Sampling for Performance", value=True, key="manufacturer_sampling")
    sample_size = st.sidebar.slider("Select Sample Size", min_value=1000, max_value=50000, step=1000, value=10000,
                                    key="manufacturer_sample_size")
    aggregation_level = st.sidebar.selectbox("📅 Select Aggregation Level", ["None", "Monthly", "Quarterly", "Yearly"],
                                             key="manufacturer_aggregation")

    # Filter Data Based on Selection
    if selected_manufacturer != "All":
        filtered_data = merged_df[merged_df['manufacturer'] == selected_manufacturer].copy()
    else:
        filtered_data = merged_df.copy()

    # Apply Aggregation
    if aggregation_level == "Monthly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('M').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'manufacturer']).agg({
            'covid_doses_cumulative': 'median'
        }).reset_index()
    elif aggregation_level == "Quarterly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Q').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'manufacturer']).agg({
            'covid_doses_cumulative': 'median'
        }).reset_index()
    elif aggregation_level == "Yearly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Y').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'manufacturer']).agg({
            'covid_doses_cumulative': 'median'
        }).reset_index()
    else:
        aggregated_data = filtered_data.copy()

    # Apply Sampling
    if sample_data and len(aggregated_data) > sample_size:
        aggregated_data = aggregated_data.sample(n=sample_size, random_state=42)
        st.info(f"Data has been sampled to {sample_size} records for improved performance.")

    # Check if data is empty after filtering
    if aggregated_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Plot Generation with Enhanced Line Plot
        fig = get_line_plot(
            data=aggregated_data,
            x_col='time_period',
            y_col='covid_doses_cumulative',
            color_col='manufacturer',
            title='COVID-19 Cumulative Doses by Manufacturer Over Time',
            labels={
                'time_period': 'Time Period',
                'covid_doses_cumulative': 'Cumulative Doses',
                'manufacturer': 'Manufacturer'
            },
            facet_col=None  # Set to 'manufacturer' if you want to facet by manufacturer
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Additional Feature: Manufacturer Contribution Analysis
    st.markdown("### 📊 Manufacturer Contribution Analysis")
    contribution = merged_df.groupby('manufacturer')['covid_doses_cumulative'].sum().reset_index()
    contribution = contribution.sort_values('covid_doses_cumulative', ascending=False)

    # Handle cases where there are fewer than 10 manufacturers
    top_n = min(10, len(contribution))
    top_contribution = contribution.head(top_n)

    fig_contribution = get_bar_chart(
        data=top_contribution,
        x_col='manufacturer',
        y_col='covid_doses_cumulative',
        title='Top Manufacturers by Cumulative Doses',
        labels={'manufacturer': 'Manufacturer', 'covid_doses_cumulative': 'Cumulative Doses'}
    )
    if fig_contribution:
        st.plotly_chart(fig_contribution, use_container_width=True)

    # Display Summary Statistics
    st.markdown("### 🔍 Data Overview")

    # Summary Statistics
    st.markdown("**Summary Statistics for Selected Data:**")
    st.write(aggregated_data[['covid_doses_cumulative']].describe())

    # Sample Data
    if 'country' in merged_df.columns:
        st.markdown("**Sample Data Points:**")
        st.dataframe(aggregated_data[['time_period', 'manufacturer', 'covid_doses_cumulative']].head(20))
    else:
        st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Health Expenditure Tab
# ----------------------------

elif tabs == "💰 Health Expenditure":
    st.title("💰 Health Expenditure (% of GDP) vs Daily COVID-19 Deaths per Million")

    # Interactive Year Selection
    years = sorted(merged_df['year'].dropna().unique().tolist())
    if not years:
        st.warning("Year data is not available.")
    else:
        selected_year = st.selectbox("Select Year", years, index=len(years) - 1)

        # Additional Filters: Sampling
        st.sidebar.subheader("⚙️ Performance Settings")
        sample_data = st.sidebar.checkbox("🔍 Enable Data Sampling for Performance", value=True, key="health_sampling")
        sample_size = st.sidebar.slider("Select Sample Size", min_value=1000, max_value=50000, step=1000, value=10000,
                                        key="health_sample_size")

        # Filter Data Based on Selection
        filtered_data = merged_df[merged_df['year'] == selected_year].copy()

        if filtered_data.empty:
            st.warning("No data available for the selected year.")
        else:
            # Apply Sampling
            if sample_data and len(filtered_data) > sample_size:
                filtered_data = filtered_data.sample(n=sample_size, random_state=42)
                st.info(f"Data has been sampled to {sample_size} records for improved performance.")

            # Plot Generation with Enhanced Scatter Plot
            fig = get_facet_scatter_plot(
                data=filtered_data,
                x_col='health_expenditure_percentage_gdp',
                y_col='daily_deaths_per_million',
                color_col='world_region',
                facet_col=None,  # Set to 'world_region' for faceting by region
                title=f'Health Expenditure vs Daily COVID-19 Deaths per Million ({selected_year})',
                labels={
                    'health_expenditure_percentage_gdp': 'Health Expenditure (% of GDP)',
                    'daily_deaths_per_million': 'Daily Deaths per Million',
                    'world_region': 'World Region'
                }
            )
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Additional Feature: Correlation Coefficient
            corr = filtered_data['health_expenditure_percentage_gdp'].corr(filtered_data['daily_deaths_per_million'])
            st.write(f"### 📈 Correlation Coefficient: {corr:.2f}")

            # Display Summary Statistics
            st.markdown("### 🔍 Data Overview")

            # Summary Statistics
            st.markdown("**Summary Statistics for Selected Data:**")
            st.write(filtered_data[['health_expenditure_percentage_gdp', 'daily_deaths_per_million']].describe())

            # Sample Data
            if 'country' in merged_df.columns:
                st.markdown("**Sample Data Points:**")
                st.dataframe(filtered_data[['country', 'day', 'health_expenditure_percentage_gdp',
                                            'daily_deaths_per_million']].head(20))
            else:
                st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Correlation Analysis Tab
# ----------------------------

elif tabs == "📈 Correlation Analysis":
    st.title("📈 Correlation Heatmap of Key Metrics")

    # Generate Correlation Heatmap
    correlation_heatmap_path = get_correlation_heatmap(merged_df)

    if correlation_heatmap_path and os.path.exists(correlation_heatmap_path):
        st.image(correlation_heatmap_path, use_container_width=True)
    else:
        st.warning("Correlation Heatmap plot not found or could not be generated.")

    # Additional Feature: Display Correlation Matrix Data
    st.subheader("📊 Correlation Matrix Data")
    correlation = merged_df[
        ['covid_doses_per_hundred', 'daily_deaths_per_million', 'health_expenditure_percentage_gdp']].corr()
    st.dataframe(correlation)

    # Display Summary Statistics
    st.markdown("### 🔍 Data Overview")

    # Summary Statistics
    st.markdown("**Summary Statistics for Key Metrics:**")
    st.write(merged_df[['covid_doses_per_hundred', 'daily_deaths_per_million',
                        'health_expenditure_percentage_gdp']].describe())

    # Sample Data
    if 'country' in merged_df.columns:
        st.markdown("**Sample Data Points:**")
        st.dataframe(merged_df[['country', 'day', 'covid_doses_per_hundred', 'daily_deaths_per_million',
                                'health_expenditure_percentage_gdp']].head(20))
    else:
        st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Regional Insights Tab
# ----------------------------

elif tabs == "🌍 Regional Insights":
    st.title("🌍 Time Series of COVID Deaths per Million by Region")

    # Interactive Region Selection
    regions = ["All"] + sorted(merged_df['world_region'].dropna().unique().tolist())
    selected_region = st.selectbox("Select World Region", regions, key="regional_region")

    # Additional Filters: Sampling and Aggregation
    st.sidebar.subheader("⚙️ Performance Settings")
    sample_data = st.sidebar.checkbox("🔍 Enable Data Sampling for Performance", value=True, key="regional_sampling")
    sample_size = st.sidebar.slider("Select Sample Size", min_value=1000, max_value=50000, step=1000, value=10000,
                                    key="regional_sample_size")
    aggregation_level = st.sidebar.selectbox("📅 Select Aggregation Level", ["None", "Monthly", "Quarterly", "Yearly"],
                                             key="regional_aggregation")

    # Filter Data Based on Selection
    if selected_region != "All":
        filtered_data = merged_df[merged_df['world_region'] == selected_region].copy()
    else:
        filtered_data = merged_df.copy()

    # Apply Aggregation
    if aggregation_level == "Monthly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('M').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'daily_deaths_per_million': 'median'
        }).reset_index()
    elif aggregation_level == "Quarterly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Q').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'daily_deaths_per_million': 'median'
        }).reset_index()
    elif aggregation_level == "Yearly":
        filtered_data['time_period'] = filtered_data['day'].dt.to_period('Y').dt.to_timestamp()
        aggregated_data = filtered_data.groupby(['time_period', 'world_region']).agg({
            'daily_deaths_per_million': 'median'
        }).reset_index()
    else:
        aggregated_data = filtered_data.copy()

    # Apply Sampling
    if sample_data and len(aggregated_data) > sample_size:
        aggregated_data = aggregated_data.sample(n=sample_size, random_state=42)
        st.info(f"Data has been sampled to {sample_size} records for improved performance.")

    # Check if data is empty after filtering
    if aggregated_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Plot Generation with Enhanced Line Plot
        fig = get_line_plot(
            data=aggregated_data,
            x_col='time_period',
            y_col='daily_deaths_per_million',
            color_col='world_region',
            title='Time Series of Daily COVID-19 Deaths per Million by World Region',
            labels={
                'time_period': 'Time Period',
                'daily_deaths_per_million': 'Daily Deaths per Million',
                'world_region': 'World Region'
            },
            facet_col=None  # Set to 'world_region' if you want to facet by region
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

    # Additional Feature: Highlight Significant Increases
    st.markdown("### 📈 Significant Increases in Death Rates")
    # Example: Identify regions with more than 10% increase over the year
    try:
        yearly_data = merged_df.copy()
        yearly_data['year'] = yearly_data['day'].dt.year
        comparison = yearly_data.groupby(['world_region', 'year']).agg(
            {'daily_deaths_per_million': 'median'}).reset_index()
        comparison['prev_year_deaths'] = comparison.groupby('world_region')['daily_deaths_per_million'].shift(1)
        comparison['pct_change'] = ((comparison['daily_deaths_per_million'] - comparison['prev_year_deaths']) /
                                    comparison['prev_year_deaths']) * 100
        significant_increases = comparison[comparison['pct_change'] > 10].dropna()

        if not significant_increases.empty:
            st.write(significant_increases[['world_region', 'year', 'pct_change']])
        else:
            st.write("No significant increases (>10%) detected in any region for the selected period.")
    except Exception as e:
        logging.error(f"Error identifying significant increases: {e}")
        st.error("An error occurred while identifying significant increases.")

    # Display Summary Statistics
    st.markdown("### 🔍 Data Overview")

    # Summary Statistics
    st.markdown("**Summary Statistics for Selected Data:**")
    st.write(aggregated_data['daily_deaths_per_million'].describe())

    # Sample Data
    if 'country' in merged_df.columns:
        st.markdown("**Sample Data Points:**")
        st.dataframe(aggregated_data[['time_period', 'world_region', 'daily_deaths_per_million']].head(20))
    else:
        st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Distribution Analysis Tab
# ----------------------------

elif tabs == "📉 Distribution Analysis":
    st.title("📉 Distribution of COVID-19 Doses per Hundred")

    # Interactive Dose Range Selection
    min_doses = int(merged_df['covid_doses_per_hundred'].min())
    max_doses = int(merged_df['covid_doses_per_hundred'].max())
    selected_range = st.slider("Select COVID Doses Range", min_value=min_doses, max_value=max_doses,
                               value=(min_doses, max_doses))

    # Filter Data Based on Selection
    filtered_data = merged_df[
        (merged_df['covid_doses_per_hundred'] >= selected_range[0]) &
        (merged_df['covid_doses_per_hundred'] <= selected_range[1])
        ].copy()

    if filtered_data.empty:
        st.warning("No data available for the selected dose range.")
    else:
        # Apply Sampling
        st.sidebar.subheader("⚙️ Performance Settings")
        sample_data = st.sidebar.checkbox("🔍 Enable Data Sampling for Performance", value=True,
                                          key="distribution_sampling")
        sample_size = st.sidebar.slider("Select Sample Size", min_value=1000, max_value=50000, step=1000, value=10000,
                                        key="distribution_sample_size")
        if sample_data and len(filtered_data) > sample_size:
            filtered_data = filtered_data.sample(n=sample_size, random_state=42)
            st.info(f"Data has been sampled to {sample_size} records for improved performance.")

        # Plot Generation with Enhanced Histogram
        fig = get_histogram(
            data=filtered_data,
            x_col='covid_doses_per_hundred',
            title='Distribution of COVID-19 Doses per Hundred',
            labels={'covid_doses_per_hundred': 'COVID-19 Doses (per Hundred)', 'count': 'Frequency'}
        )
        if fig:
            st.plotly_chart(fig, use_container_width=True)

        # Additional Feature: Statistical Summary
        st.markdown("### 📊 Statistical Summary")
        summary = filtered_data['covid_doses_per_hundred'].describe()
        st.table(summary)

        # Display Summary Statistics
        st.markdown("### 🔍 Data Overview")

        # Summary Statistics
        st.markdown("**Summary Statistics for Selected Data:**")
        st.write(filtered_data['covid_doses_per_hundred'].describe())

        # Sample Data
        if 'country' in merged_df.columns:
            st.markdown("**Sample Data Points:**")
            st.dataframe(filtered_data[['country', 'day', 'covid_doses_per_hundred']].head(20))
        else:
            st.warning("'country' column not found in the DataFrame.")

# ----------------------------
# Data Inspection Tab
# ----------------------------

elif tabs == "🗃️ Data Inspection":
    st.title("🗃️ Data Inspection")

    st.markdown("""
    Use this section to inspect the raw and filtered data used in the dashboard. You can apply various filters to view specific subsets of the data.
    """)

    # Sidebar Filters
    st.sidebar.header("🔍 Data Filters")
    available_years = merged_df['year'].dropna().unique().tolist()
    if available_years:
        selected_year = st.sidebar.multiselect("Select Year(s)", options=sorted(available_years),
                                               default=sorted(available_years))
    else:
        selected_year = []

    available_regions = merged_df['world_region'].dropna().unique().tolist()
    if available_regions:
        selected_region = st.sidebar.multiselect("Select World Region(s)",
                                                 options=sorted(available_regions),
                                                 default=sorted(available_regions))
    else:
        selected_region = []

    available_countries = merged_df['country'].dropna().unique().tolist()
    if available_countries:
        selected_country = st.sidebar.multiselect("Select Country(ies)",
                                                  options=sorted(available_countries),
                                                  default=sorted(available_countries))
    else:
        selected_country = []

    # Apply Filters
    if selected_year and selected_region and selected_country:
        inspection_data = merged_df[
            (merged_df['year'].isin(selected_year)) &
            (merged_df['world_region'].isin(selected_region)) &
            (merged_df['country'].isin(selected_country))
            ]
    else:
        inspection_data = merged_df.copy()

    st.markdown("### 📊 Filtered Data")
    st.dataframe(inspection_data)

    # Provide download option
    csv = inspection_data.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv,
        file_name='filtered_covid_data.csv',
        mime='text/csv',
    )

    # Display summary statistics
    st.markdown("### 📈 Summary Statistics")
    summary = inspection_data.describe()
    st.table(summary)

    # Display specific data points if needed
    if len(inspection_data) > 100:
        st.markdown("### 📋 Sample Data Points")
        st.write("**Sample 100 Data Points:**")
        st.dataframe(
            inspection_data[['country', 'day', 'daily_deaths_per_million', 'covid_doses_per_hundred']].head(100))
    else:
        st.markdown("### 📋 Data Points")
        st.dataframe(inspection_data)

# ----------------------------
# Download Visualizations Tab
# ----------------------------

elif tabs == "📥 Download Visualizations":
    st.title("📥 Download All Visualizations")
    st.markdown("You can download all the generated visualizations below.")

    # Define a dictionary of plot names and their paths
    plots = {
        "COVID Doses vs Daily Deaths per Million": os.path.join(processed_data_path, 'covid_doses_vs_deaths.png'),
        "COVID Cumulative Doses by Top Manufacturers Over Time": os.path.join(processed_data_path,
                                                                              'doses_by_manufacturer_over_time.png'),
        "Health Expenditure vs Daily COVID Deaths per Million": os.path.join(processed_data_path,
                                                                             'health_expenditure_vs_deaths.png'),
        "Weekly Death Rates in the US by Vaccination Status": os.path.join(processed_data_path,
                                                                           'us_death_rates_interactive.html'),
        "Correlation Heatmap": os.path.join(processed_data_path, 'correlation_heatmap.png'),
        "Time Series of COVID Deaths per Million by Region": os.path.join(processed_data_path,
                                                                          'time_series_deaths_by_region.png'),
        "Distribution of COVID Doses per Hundred": os.path.join(processed_data_path, 'distribution_covid_doses.png')
    }

    for plot_name, plot_path in plots.items():
        if os.path.exists(plot_path):
            with open(plot_path, "rb") as f:
                bytes_data = f.read()
                file_extension = os.path.splitext(plot_path)[1].lower()
                if file_extension == ".png":
                    mime_type = "image/png"
                elif file_extension == ".html":
                    mime_type = "text/html"
                else:
                    mime_type = "application/octet-stream"

                st.download_button(
                    label=f"📥 Download {plot_name}",
                    data=bytes_data,
                    file_name=os.path.basename(plot_path),
                    mime=mime_type
                )
        else:
            st.warning(f"{plot_name} plot not found.")

# ----------------------------
# Handle Unrecognized Tabs
# ----------------------------

else:
    st.warning("🚫 Selected tab not recognized. Please select a valid tab from the sidebar.")

# ----------------------------
# Footer
# ----------------------------

st.markdown("---")
st.markdown(f"**Last Updated:** {datetime.now().strftime('%B %d, %Y %H:%M:%S')}")
st.markdown("**Developed by:** Your Name | **Contact:** [your.email@example.com](mailto:your.email@example.com)")
