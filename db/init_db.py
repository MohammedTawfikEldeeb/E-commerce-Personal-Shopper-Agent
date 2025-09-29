# db/setup_database.py

import sqlite3
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, 
                 db_path="db/ecommerce_products.db", 
                 csv_path="data/raw/sutra_products_cleaned.csv", # Assuming this is the new cleaned file name
                 schema_path="db/schema.sql"):
        self.db_path = db_path
        self.csv_path = csv_path
        self.schema_path = schema_path

    def initialize_schema(self):
        """Creates a fresh database and executes the schema."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        conn = sqlite3.connect(self.db_path)
        with open(self.schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        logger.info("Database schema created successfully.")
        return conn

    def load_and_insert_data(self, conn):
        """Loads data from the cleaned CSV and inserts it."""
        logger.info(f"Loading CSV data from {self.csv_path}")
        df = pd.read_csv(self.csv_path)
        logger.info(f"Loaded {len(df)} rows. Starting insertion...")
        
        insert_sql = """
        INSERT INTO products (
            category, sub_category, title, sale_price, original_price, currency,
            available_sizes, product_url, image_url, product_details_json, title_masri
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        cursor = conn.cursor()
        inserted_count = 0
        
        for _, row in df.iterrows():
            try:
                # Direct mapping from the new, clean CSV columns
                data = (
                    row.get("Category"),
                    row.get("Sub Category"),
                    row.get("Product Name"),
                    row.get("Sale Price Float"),    # Using the clean float column
                    row.get("Original Price Float"),# Using the clean float column
                    row.get("Currency"),
                    row.get("Available Sizes"),
                    row.get("Product URL"),
                    row.get("Image URL"),
                    row.get("Product Details JSON"),
                    row.get("Product Name Masri")
                )
                
                if not row.get("Product URL"):
                    continue

                cursor.execute(insert_sql, data)
                inserted_count += 1
            except Exception as e:
                logger.warning(f"Skipping row due to error: {e}")
        
        conn.commit()
        logger.info(f"Data insertion completed. Inserted: {inserted_count} rows.")

    def run(self):
        """Runs the entire database setup and data ingestion process."""
        connection = self.initialize_schema()
        self.load_and_insert_data(connection)
        connection.close()

if __name__ == '__main__':
    # Make sure your cleaned CSV file is named 'sutra_products_cleaned.csv'
    # Or change the name in the line below
    setup = DatabaseSetup(csv_path="data/raw/sutra_products_cleaned.csv")
    setup.run()