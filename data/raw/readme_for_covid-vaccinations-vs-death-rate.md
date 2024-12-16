# COVID-19 vaccinations vs. COVID-19 deaths - Data package

This data package contains the data that powers the chart ["COVID-19 vaccinations vs. COVID-19 deaths"](https://ourworldindata.org/grapher/covid-vaccinations-vs-covid-death-rate?v=1&csvType=full&useColumnShortNames=false) on the Our World in Data website.

## CSV Structure

The high level structure of the CSV file is that each row is an observation for an entity (usually a country or region) and a timepoint (usually a year).

The first two columns in the CSV file are "Entity" and "Code". "Entity" is the name of the entity (e.g. "United States"). "Code" is the OWID internal entity code that we use if the entity is a country or region. For normal countries, this is the same as the [iso alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) code of the entity (e.g. "USA") - for non-standard countries like historical countries these are custom codes.

The third column is either "Year" or "Day". If the data is annual, this is "Year" and contains only the year as an integer. If the column is "Day", the column contains a date string in the form "YYYY-MM-DD".

The remaining columns are the data columns, each of which is a time series. If the CSV data is downloaded using the "full data" option, then each column corresponds to one time series below. If the CSV data is downloaded using the "only selected data visible in the chart" option then the data columns are transformed depending on the chart type and thus the association with the time series might not be as straightforward.

## Metadata.json structure

The .metadata.json file contains metadata about the data package. The "charts" key contains information to recreate the chart, like the title, subtitle etc.. The "columns" key contains information about each of the columns in the csv, like the unit, timespan covered, citation for the data etc..

## About the data

Our World in Data is almost never the original producer of the data - almost all of the data we use has been compiled by others. If you want to re-use data, it is your responsibility to ensure that you adhere to the sources' license and to credit them correctly. Please note that a single time series may have more than one source - e.g. when we stich together data from different time periods by different producers or when we calculate per capita metrics using population data from a second source.

### How we process data at Our World In Data
All data and visualizations on Our World in Data rely on data sourced from one or several original data providers. Preparing this original data involves several processing steps. Depending on the data, this can include standardizing country names and world region definitions, converting units, calculating derived indicators such as per capita measures, as well as adding or adapting metadata such as the name or the description given to an indicator.
[Read about our data pipeline](https://docs.owid.io/projects/etl/)

## Detailed information about each time series


## Daily new COVID-19 deaths per million people
Last updated: December 16, 2024  
Next update: January 2025  
Unit: deaths per million people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
World Health Organization (2024); Population based on various sources (2024) – with major processing by Our World in Data

#### Full citation
World Health Organization (2024); Population based on various sources (2024) – with major processing by Our World in Data. “Daily new COVID-19 deaths per million people” [dataset]. World Health Organization, “COVID-19 Dashboard WHO COVID-19 Dashboard - Daily cases and deaths”; Various sources, “Population” [original data].
Source: World Health Organization (2024), Population based on various sources (2024) – with major processing by Our World In Data

### What you should know about this data

### Sources

#### World Health Organization – COVID-19 Dashboard
Retrieved on: 2024-12-16  
Retrieved from: https://covid19.who.int/  

#### Various sources – Population
Retrieved on: 2024-07-11  
Retrieved from: https://ourworldindata.org/population-sources  

#### Notes on our processing step for this indicator
This indicator is estimated by normalizing by population. We have used daily population estimates, which leads to changes in the denominator between datapoints from different days. For instance, the denominator for January 1st will be different to the one on January 2nd.


## Cumulative COVID-19 vaccinations per 100 people
Total number of COVID-19 vaccination doses administered per 100 people in the total population.
Last updated: August 14, 2024  
Unit: doses per hundred people  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Official data collated by Our World in Data (2024); World Health Organisation (2024); Population based on various sources (2024) – with major processing by Our World in Data

#### Full citation
Official data collated by Our World in Data (2024); World Health Organisation (2024); Population based on various sources (2024) – with major processing by Our World in Data. “Cumulative COVID-19 vaccinations per 100 people” [dataset]. Official data collated by Our World in Data, “COVID-19, vaccinations”; World Health Organisation, “COVID-19, vaccinations (WHO)”; Various sources, “Population” [original data].
Source: Official data collated by Our World in Data (2024), World Health Organisation (2024), Population based on various sources (2024) – with major processing by Our World In Data

### What you should know about this data

### Sources

#### Official data collated by Our World in Data – COVID-19, vaccinations
Retrieved on: 2024-08-14  
Retrieved from: https://github.com/owid/covid-19-data/  

#### World Health Organisation – COVID-19, vaccinations (WHO)
Retrieved on: 2024-08-14  
Retrieved from: https://covid19.who.int/  

#### Various sources – Population
Retrieved on: 2024-07-11  
Retrieved from: https://ourworldindata.org/population-sources  

#### Notes on our processing step for this indicator
Per-capita values have been estimated by using the population in 2022 as a reference.


## World regions according to OWID
Last updated: January 1, 2023  
Date range: 2023–2023  


### How to cite this data

#### In-line citation
If you have limited space (e.g. in data visualizations), you can use this abbreviated in-line citation:  
Our World in Data – processed by Our World in Data

#### Full citation
Our World in Data – processed by Our World in Data. “World regions according to OWID” [dataset]. Our World in Data, “Regions” [original data].
Source: Our World in Data

### What you should know about this data

### Source

#### Our World in Data – Regions


    