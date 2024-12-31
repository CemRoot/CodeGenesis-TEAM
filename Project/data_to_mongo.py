import os
import sys
import certifi
import logging
import json
from datetime import datetime
from typing import Dict
import csv

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
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
LOG_DIR = "../reports/logs"  # Local writable directory
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

def detect_delimiter(file_path: str) -> str:
    try:
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            sample = csvfile.read(1024)
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample)
            delimiter = dialect.delimiter
            logger.info(f"Detected delimiter '{delimiter}' for file: {file_path}")
            return delimiter
    except Exception as e:
        logger.warning(f"Could not detect delimiter for file: {file_path}. Defaulting to comma. Error: {e}")
        return ","

def validate_csv_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        logger.error(f"No read access to file: {file_path}")
        return False
    return True

def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        if "date" in column.lower() or "time" in column.lower():
            try:
                df[column] = pd.to_datetime(df[column], errors="coerce")
                df[column] = df[column].replace({pd.NaT: None})
                logger.info(f"Converted '{column}' to datetime.")
            except Exception as e:
                logger.warning(f"Failed to convert '{column}' to datetime: {e}")
    return df

def load_csv_to_mongo(client: MongoClient, db_name: str, file_path: str, collection_name: str, batch_size: int = 1000):
    if not validate_csv_file(file_path):
        return

    try:
        delimiter = detect_delimiter(file_path)
        df = pd.read_csv(file_path, delimiter=delimiter, encoding="utf-8", engine="python")
        logger.info(f"Loaded {len(df)} records from {file_path}.")

        df = df.where(pd.notnull(df), None)
        df = convert_datetime_columns(df)
        data_records = df.to_dict(orient="records")

        db = client[db_name]
        collection = db.get_collection(collection_name, write_concern=WriteConcern("majority"))

        for i in range(0, len(data_records), batch_size):
            batch = data_records[i:i + batch_size]
            try:
                collection.insert_many(batch, ordered=False)
                logger.info(f"Inserted batch {i // batch_size + 1} of size {len(batch)} into '{collection_name}'.")
            except errors.BulkWriteError as bwe:
                logger.error(f"BulkWriteError on batch {i // batch_size + 1}: {bwe.details}")
            except Exception as e:
                logger.error(f"Error inserting batch {i // batch_size + 1}: {e}")

        logger.info(f"Completed migration for '{file_path}' into '{collection_name}'.")

    except Exception as e:
        logger.critical(f"Critical error during migration of '{file_path}': {e}")

# ================================================================
# MAIN FUNCTION
# ================================================================

def main():
    csv_files = {
        "../data/raw/covid-vaccinations-vs-covid-death-rate.csv": "covid_vacc_death_rate",
        "../data/raw/covid-vaccine-doses-by-manufacturer.csv": "covid_vacc_manufacturer",
        "../data/raw/OECD_health_expenditure.csv": "oecd_health_expenditure",
        "../data/raw/united-states-rates-of-covid-19-deaths-by-vaccination-status.csv": "us_death_rates",
    }

    print("Select an option:")
    print("0. Load all data")
    for i, (file_path, collection_name) in enumerate(csv_files.items(), start=1):
        print(f"{i}. {file_path} -> {collection_name}")

    try:
        choice = int(input("Your choice: "))
        if choice == 0:
            logger.info("Selected option: Load all data.")
            with MongoClient(MONGO_URI, tlsCAFile=certifi.where()) as client:
                for file_path, collection_name in csv_files.items():
                    logger.info(f"Loading data from {file_path} into collection {collection_name}.")
                    load_csv_to_mongo(client, DATABASE_NAME, file_path, collection_name)
            logger.info("All data loaded successfully.")
        elif 1 <= choice <= len(csv_files):
            file_path, collection_name = list(csv_files.items())[choice - 1]
            logger.info(f"Selected file: {file_path}, collection: {collection_name}")
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