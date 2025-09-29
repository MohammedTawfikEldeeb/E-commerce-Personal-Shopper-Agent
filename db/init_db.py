# db/setup_database.py

import sqlite3
import pandas as pd
import logging
import os
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, 
                 db_path="db/ecommerce_products.db", 
                 csv_path="data/raw/sutra_products_cleaned.csv", 
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

    def convert_price_string(self, price_str):
        """Convert price string to float, handling various formats."""
        if not isinstance(price_str, str):
            return price_str
        
        # Handle "From" prices by extracting the numeric part
        if price_str.startswith('From '):
            price_str = price_str[5:]  # Remove "From " prefix
            
        # Remove currency symbols and commas
        price_str = price_str.replace('LE', '').replace('₹', '').replace(',', '').strip()
        
        # Handle empty or invalid strings
        if not price_str or price_str.lower() in ['none', 'null', 'n/a']:
            return None
            
        try:
            return float(price_str)
        except ValueError:
            logger.warning(f"Could not convert price string '{price_str}' to float")
            return None

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
        product_urls_seen = set()
        
        for _, row in df.iterrows():
            try:
                # Skip rows without product URL
                if not row.get("Product URL"):
                    continue
                    
                # Skip duplicate product URLs
                product_url = row.get("Product URL")
                if product_url in product_urls_seen:
                    continue
                product_urls_seen.add(product_url)
                
                # Direct mapping from the new, clean CSV columns
                data = (
                    row.get("Category"),
                    row.get("Sub Category"),
                    row.get("Product Name"),
                    row.get("Sale Price"),    # Fixed column name
                    row.get("Original Price"), # Fixed column name
                    row.get("Currency"),
                    row.get("Available Sizes"),
                    product_url,
                    row.get("Image URL"),
                    row.get("Product Details JSON"),
                    row.get("Product Name Masri")
                )
                
                # Convert price strings to float values
                sale_price = data[3]
                original_price = data[4]
                
                # Handle price conversion with improved logic
                sale_price = self.convert_price_string(sale_price)
                original_price = self.convert_price_string(original_price)
                
                # Update the data tuple with converted prices
                data = (
                    data[0],  # Category
                    data[1],  # Sub Category
                    data[2],  # Product Name
                    sale_price,    # Converted Sale Price
                    original_price, # Converted Original Price
                    data[5],  # Currency
                    data[6],  # Available Sizes
                    data[7],  # Product URL
                    data[8],  # Image URL
                    data[9],  # Product Details JSON
                    data[10]  # Product Name Masri
                )
                
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