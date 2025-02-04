import os
import sys
import certifi
import logging
import json
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from logging.handlers import RotatingFileHandler

# ================================================================
# CONFIGURATIONS
# ================================================================

# Load environment variables from the .env file
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise EnvironmentError("Please define MONGO_URI and DATABASE_NAME in the .env file.")

# Ensure the log directory exists
LOG_DIR = "../reports/logs" # Local writable directory
os.makedirs(LOG_DIR, exist_ok=True)

# Log file configuration
LOG_FILE = os.path.join(LOG_DIR, f"data_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# Set up logger
logger = logging.getLogger("DataMigrationLogger")
logger.setLevel(logging.INFO)

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "filename": record.pathname,
            "line_no": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# File handler for logs
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
file_formatter = JSONFormatter()
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Stream handler for console output
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(file_formatter)
logger.addHandler(stream_handler)

logger.info("Logger setup complete. Logs will be written to '%s'.", LOG_FILE)

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Makes column names compatible with MongoDB:
    - Replaces spaces and special characters with underscores.
    - Converts double underscores to single underscores.
    - Removes leading and trailing underscores.
    """
    df.columns = df.columns.str.replace(r"[^a-zA-Z0-9_]", "_", regex=True)
    df.columns = df.columns.str.replace(r"__+", "_", regex=True)  # Double underscores are converted to single underscores
    df.columns = df.columns.str.strip("_")  # Leading and trailing underscores are removed
    return df

def validate_csv_file(file_path: str) -> bool:
    """
    Checks the existence and accessibility of the CSV file.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        logger.error(f"No read access to file: {file_path}")
        return False
    return True

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the DataFrame:
    - Trims leading and trailing spaces from string cells.
    - Replaces NaN values with None.
    """
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].map(lambda x: str(x).strip() if isinstance(x, str) else x)
    df = df.where(pd.notnull(df), None)
    return df

def load_csv_to_mongo(client, db_name, file_path, collection_name):
    """
    Reads and cleans a CSV file and transfers it to MongoDB.
    """
    if not validate_csv_file(file_path):
        return

    try:
        # Load the CSV file
        df = pd.read_csv(file_path, delimiter=",", encoding="utf-8", engine="python")
        logger.info(f"Loaded {len(df)} records from {file_path}.")

        # Clean column names
        df = clean_column_names(df)

        # Data cleaning
        df = clean_dataframe(df)

        # Data verification before transferring to MongoDB
        logger.info(f"DataFrame columns: {list(df.columns)}")
        logger.info(f"Sample data:\n{df.head()}")

        # Convert DataFrame to dictionary format and transfer to MongoDB
        data_records = df.to_dict(orient="records")
        db = client[db_name]
        collection = db[collection_name]
        collection.insert_many(data_records)
        logger.info(f"{len(data_records)} records successfully inserted into '{collection_name}'.")

    except Exception as e:
        logger.error(f"Error during data migration: {e}")

# ================================================================
# MAIN FUNCTION
# ================================================================

def main():
    base_path = "/Users/dr.sam/Desktop/CodeGenesis-TEAM/data/raw"  # Base directory
    csv_files = {
        "covid-vaccinations-vs-covid-death-rate.csv": "covid_vacc_death_rate",
        "covid-vaccine-doses-by-manufacturer.csv": "covid_vacc_manufacturer",
        "united-states-rates-of-covid-19-deaths-by-vaccination-status.csv": "us_death_rates",
    }

    print("Select an option:")
    print("0. Load all data")
    for i, (file_name, collection_name) in enumerate(csv_files.items(), start=1):
        print(f"{i}. {file_name} -> {collection_name}")

    try:
        choice = int(input("Your choice: "))
        if choice == 0:
            logger.info("Selected option: Load all data.")
            with MongoClient(MONGO_URI, tlsCAFile=certifi.where()) as client:
                for file_name, collection_name in csv_files.items():
                    file_path = os.path.join(base_path, file_name)
                    load_csv_to_mongo(client, DATABASE_NAME, file_path, collection_name)
            logger.info("All data loaded successfully.")
        elif 1 <= choice <= len(csv_files):
            file_name, collection_name = list(csv_files.items())[choice - 1]
            file_path = os.path.join(base_path, file_name)
            with MongoClient(MONGO_URI, tlsCAFile=certifi.where()) as client:
                load_csv_to_mongo(client, DATABASE_NAME, file_path, collection_name)
        else:
            print("Invalid selection.")
    except ValueError:
        print("Please enter a number.")
    except Exception as e:
        logger.error(f"Error during menu execution: {e}")

    logger.info("Migration completed.")

# ================================================================
# ENTRY POINT
# ================================================================

if __name__ == "__main__":
    start_time = datetime.now()
    logger.info("Migration process started.")
    main()
    end_time = datetime.now()
    logger.info(f"Migration process completed in {end_time - start_time}.")