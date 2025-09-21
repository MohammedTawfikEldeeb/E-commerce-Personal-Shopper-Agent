
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    row_index INTEGER,
    product_id VARCHAR(255) UNIQUE NOT NULL,
    pid VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    brand VARCHAR(255),
    category VARCHAR(255) NOT NULL,
    sub_category VARCHAR(255) NOT NULL,
    description TEXT,
    actual_price DECIMAL(10,2),
    selling_price DECIMAL(10,2),
    discount_percentage VARCHAR(50),
    average_rating DECIMAL(3,2),
    out_of_stock BOOLEAN NOT NULL DEFAULT FALSE,
    seller VARCHAR(255),
    url TEXT NOT NULL UNIQUE,
    images TEXT,
    product_details TEXT,
    crawled_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
