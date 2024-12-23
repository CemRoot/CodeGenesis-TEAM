import os
import sys
import certifi
import logging
import json
from datetime import datetime
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv

import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient, errors
from pymongo.write_concern import WriteConcern
from pymongo.read_concern import ReadConcern
# from pymongo import ASCENDING  # Uncomment if you need to create indexes
from logging.handlers import RotatingFileHandler

# ================================================================
# CONFIGURATIONS
# ================================================================

# Load environment variables from the .env file
load_dotenv()

# MongoDB connection settings from environment variables
MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

if not MONGO_URI or not DATABASE_NAME:
    raise EnvironmentError("Please define MONGO_URI and DATABASE_NAME in the .env file.")

# Logging configuration
LOG_DIR = "/reports"
LOG_FILE = os.path.join(LOG_DIR, f"data_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

# Create the reports directory if it does not exist
os.makedirs(LOG_DIR, exist_ok=True)

# Set up logger
logger = logging.getLogger("DataMigrationLogger")
logger.setLevel(logging.INFO)

# Custom JSON Formatter
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "name": record.name,
            "filename": record.pathname,
            "line_no": record.lineno,
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# File handler for JSON logs with rotation
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)
file_formatter = JSONFormatter()
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# Stream handler to output logs to console in JSON format
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(file_formatter)
logger.addHandler(stream_handler)

# ================================================================
# HELPER FUNCTIONS
# ================================================================

def detect_delimiter(file_path: str) -> str:
    """
    Detect the delimiter of a CSV file using csv.Sniffer.

    :param file_path: Path to the CSV file.
    :return: The detected delimiter as a string, or ',' if detection fails.
    """
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
    """
    Check if the CSV file exists and is readable.

    :param file_path: Path to the CSV file.
    :return: True if the file exists and is readable; False otherwise.
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    if not os.access(file_path, os.R_OK):
        logger.error(f"No read access to file: {file_path}")
        return False
    return True

def convert_datetime_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert columns containing 'date' or 'time' in their names to datetime objects.
    Replace any NaT values with None for MongoDB compatibility.

    :param df: Pandas DataFrame to process.
    :return: Modified Pandas DataFrame with datetime columns.
    """
    for column in df.columns:
        col_lower = column.lower()
        if "date" in col_lower or "time" in col_lower:
            try:
                # Remove deprecated 'infer_datetime_format' parameter
                df[column] = pd.to_datetime(df[column], errors="coerce")

                # Replace NaT with None
                df[column] = df[column].replace({pd.NaT: None})

                num_invalid = df[column].isna().sum()
                if num_invalid > 0:
                    logger.warning(
                        f"'{column}' column has {num_invalid} invalid date/time entries set to None."
                    )
                else:
                    logger.info(f"'{column}' column successfully converted to datetime format.")
            except Exception as e:
                logger.warning(f"Error converting '{column}' to datetime: {e}")

    return df

def load_csv_to_mongo(
    client: MongoClient,
    db_name: str,
    file_path: str,
    collection_name: str,
    batch_size: int = 1000
) -> None:
    """
    Load data from a CSV file into a MongoDB collection.

    :param client: A MongoClient instance.
    :param db_name: Name of the target MongoDB database.
    :param file_path: Path to the CSV file.
    :param collection_name: Name of the target MongoDB collection.
    :param batch_size: Number of records to insert per batch.
    """
    if not validate_csv_file(file_path):
        return

    logger.info(f"Starting migration for file: {file_path}")

    try:
        # Detect CSV delimiter
        delimiter = detect_delimiter(file_path)

        # Read the CSV file with the detected delimiter
        df = pd.read_csv(file_path, delimiter=delimiter, encoding="utf-8", engine="python")
        logger.info(f"Successfully read {len(df)} records from {file_path}.")

        # Replace NaN with None for MongoDB compatibility
        df = df.where(pd.notnull(df), None)

        # Convert date/time columns
        df = convert_datetime_columns(df)

        # Convert DataFrame to a list of dictionaries
        data_records = df.to_dict(orient="records")
        logger.info(f"Converted data to JSON format for insertion into '{collection_name}' collection.")

        # Connect to MongoDB collection with write and read concerns
        db = client[db_name]
        collection = db.get_collection(
            collection_name,
            write_concern=WriteConcern("majority"),
            read_concern=ReadConcern("majority")
        )

        total_inserted = 0
        total_errors = 0

        # Insert data in batches
        for i in range(0, len(data_records), batch_size):
            batch = data_records[i : i + batch_size]
            try:
                result = collection.insert_many(batch, ordered=False)
                inserted_count = len(result.inserted_ids)
                total_inserted += inserted_count
                logger.info(
                    f"Batch {i // batch_size + 1}: Inserted {inserted_count} records into '{collection_name}'."
                )
            except errors.BulkWriteError as bwe:
                write_errors = bwe.details.get("writeErrors", [])
                total_errors += len(write_errors)
                logger.error(
                    f"Batch {i // batch_size + 1}: Bulk write error. "
                    f"Problematic records: {len(write_errors)}. Details: {write_errors}"
                )
            except Exception as e:
                total_errors += len(batch)
                logger.error(
                    f"Batch {i // batch_size + 1}: General error during insertion: {e}. "
                    f"Failed records: {len(batch)}."
                )

        logger.info(
            f"Completed migration for '{file_path}'. Total inserted: {total_inserted}, Total errors: {total_errors}."
        )

        # Post-insertion validation
        try:
            count_in_db = collection.estimated_document_count()
            expected_count = len(data_records)
            if count_in_db >= expected_count - total_errors:
                logger.info(
                    f"Data validation successful: At least {expected_count - total_errors} records "
                    f"inserted into '{collection_name}'."
                )
            else:
                logger.warning(
                    f"Data validation failed: Expected at least {expected_count - total_errors} records "
                    f"in '{collection_name}', found {count_in_db}."
                )
        except Exception as e:
            logger.error(f"Error during post-insertion validation: {e}")

    except Exception as e:
        logger.critical(f"Critical error during migration of '{file_path}': {e}")

# ================================================================
# MAIN FUNCTION
# ================================================================

def main():
    """
    Main function to initiate data migration for specified CSV files.
    Provides a simple menu to select which CSV file to process.
    """
    # Define CSV files and their corresponding MongoDB collections
    csv_files: Dict[str, Dict[str, str]] = {
        "/Users/dr.sam/Desktop/CodeGenesis-TEAM/data/raw/covid-vaccinations-vs-covid-death-rate.csv": {
            "collection": "covid_vacc_death_rate"
        },
        "/Users/dr.sam/Desktop/CodeGenesis-TEAM/data/raw/covid-vaccine-doses-by-manufacturer.csv": {
            "collection": "covid_vacc_manufacturer"
        },
        "/Users/dr.sam/Desktop/CodeGenesis-TEAM/data/raw/OECD_health_expenditure.csv": {
            "collection": "oecd_health_expenditure"
        },
        "/Users/dr.sam/Desktop/CodeGenesis-TEAM/data/raw/united-states-rates-of-covid-19-deaths-by-vaccination-status.csv": {
            "collection": "us_death_rates"
        }
    }

    # Display a menu so the user can choose which CSV file to load
    choices = list(csv_files.items())
    print("Please select the CSV file you want to load:")
    for i, (path, details) in enumerate(choices, start=1):
        print(f"{i}. {path} -> collection='{details['collection']}'")

    try:
        user_choice = int(input("Your choice: "))
        if not (1 <= user_choice <= len(choices)):
            print("Invalid selection!")
            return
    except ValueError:
        print("Please enter a valid number.")
        return

    # Retrieve the selected file path and collection name
    file_path, details = choices[user_choice - 1]
    collection_name = details.get("collection")

    logger.info(f"Selected file: {file_path}, collection: {collection_name}")

    # Create the MongoDB client
    with MongoClient(MONGO_URI, tlsCAFile=certifi.where()) as client:
        # Load the selected CSV into MongoDB
        load_csv_to_mongo(
            client=client,
            db_name=DATABASE_NAME,
            file_path=file_path,
            collection_name=collection_name
        )

    logger.info("Data transfer has been completed.")

# ================================================================
# ENTRY POINT
# ================================================================
if __name__ == "__main__":
    start_time = datetime.now()
    logger.info("Data migration process started.")
    main()
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Data migration process completed. Duration: {duration}")