-- db/schema.sql

DROP TABLE IF EXISTS products;

CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT,
    sub_category TEXT,
    title TEXT NOT NULL,          -- From 'Product Name'
    sale_price REAL,              -- From 'Sale Price Float'
    original_price REAL,          -- From 'Original Price Float'
    currency TEXT,
    available_sizes TEXT,
    product_url TEXT UNIQUE NOT NULL,
    image_url TEXT,
    product_details_json TEXT,
    title_masri TEXT
);