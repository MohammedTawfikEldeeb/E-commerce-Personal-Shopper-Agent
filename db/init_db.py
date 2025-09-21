import sqlite3
import pandas as pd
import json
import re
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    def __init__(self, db_path="ecommerce_products.db", excel_path="../data/raw/output.xlsx"):
        self.db_path = db_path
        self.excel_path = excel_path
        self.schema_path = "schema.sql"
        
    def clean_price(self, price_str):
        """Clean and convert price string to float"""
        if pd.isna(price_str) or price_str == "":
            return None
        price_clean = re.sub(r"[^\d.]", "", str(price_str))
        try:
            return float(price_clean)
        except ValueError:
            return None
    
    def parse_datetime(self, datetime_str):
        """Parse datetime string from Excel format"""
        if pd.isna(datetime_str):
            return None
        try:
            dt = pd.to_datetime(datetime_str, format="%d/%m/%Y, %H:%M:%S")
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            try:
                dt = pd.to_datetime(datetime_str)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return None
    
    def clean_json_field(self, field_value):
        """Clean and format JSON fields"""
        if pd.isna(field_value):
            return None
        if isinstance(field_value, str):
            try:
                parsed = json.loads(field_value)
                return json.dumps(parsed)
            except:
                return field_value
        else:
            return json.dumps(field_value)
    
    def create_database(self):
        """Create the database and apply schema"""
        logger.info(f"Creating database at {self.db_path}")
        with open(self.schema_path, "r") as f:
            schema_sql = f.read()
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        logger.info("Database schema created successfully")
        return conn
    
    def load_excel_data(self):
        """Load and process Excel data"""
        logger.info(f"Loading Excel data from {self.excel_path}")
        df = pd.read_excel(self.excel_path)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        return df
    
    def process_and_insert_data(self, conn, df):
        """Process Excel data and insert into database"""
        logger.info("Processing and inserting data into database")
        cursor = conn.cursor()
        
        insert_sql = """
        INSERT INTO products (
            row_index, product_id, pid, title, brand, category, sub_category,
            description, actual_price, selling_price, discount_percentage,
            average_rating, out_of_stock, seller, url, images, product_details, crawled_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        inserted_count = 0
        skipped_count = 0
        
        for index, row in df.iterrows():
            try:
                data = (
                    row["Unnamed: 0"],  # row_index
                    row["_id"],  # product_id
                    row["pid"],  # pid
                    row["title"],
                    row["brand"] if not pd.isna(row["brand"]) else None,
                    row["category"],
                    row["sub_category"],
                    row["description"] if not pd.isna(row["description"]) else None,
                    self.clean_price(row["actual_price"]),
                    self.clean_price(row["selling_price"]),
                    row["discount"] if not pd.isna(row["discount"]) else None,
                    row["average_rating"] if not pd.isna(row["average_rating"]) else None,
                    bool(row["out_of_stock"]),
                    row["seller"] if not pd.isna(row["seller"]) else None,
                    row["url"],
                    self.clean_json_field(row["images"]),
                    self.clean_json_field(row["product_details"]),
                    self.parse_datetime(row["crawled_at"]),
                )
                cursor.execute(insert_sql, data)
                inserted_count += 1
            except Exception as e:
                logger.warning(f"Skipping row {index} due to error: {e}")
                skipped_count += 1
                continue
        
        conn.commit()
        logger.info(f"Data insertion completed. Inserted: {inserted_count}, Skipped: {skipped_count}")
        return inserted_count, skipped_count
    
    def initialize(self):
        """Main initialization method"""
        logger.info("Starting database initialization")
        conn = self.create_database()
        df = self.load_excel_data()
        self.process_and_insert_data(conn, df)
        conn.close()
        logger.info("Database initialization completed successfully!")

def main():
    initializer = DatabaseInitializer()
    initializer.initialize()

if __name__ == "__main__":
    main()
