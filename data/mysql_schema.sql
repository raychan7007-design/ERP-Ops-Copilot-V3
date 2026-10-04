-- MySQL 8.x design draft corresponding to the SQLite demo.
CREATE TABLE products(sku VARCHAR(32) PRIMARY KEY,product_name VARCHAR(128) NOT NULL,category VARCHAR(64) NOT NULL,safety_stock INT NOT NULL);
CREATE TABLE suppliers(supplier_id VARCHAR(32) PRIMARY KEY,supplier_name VARCHAR(128) NOT NULL);
CREATE TABLE purchase_orders(po_id VARCHAR(32) PRIMARY KEY,supplier_id VARCHAR(32) NOT NULL,status VARCHAR(32) NOT NULL,created_at DATETIME NOT NULL,FOREIGN KEY(supplier_id) REFERENCES suppliers(supplier_id));
CREATE TABLE purchase_order_items(po_id VARCHAR(32),sku VARCHAR(32),ordered_qty INT NOT NULL,received_qty INT NOT NULL DEFAULT 0,PRIMARY KEY(po_id,sku),FOREIGN KEY(po_id) REFERENCES purchase_orders(po_id),FOREIGN KEY(sku) REFERENCES products(sku));
CREATE TABLE sales_orders(so_id VARCHAR(32) PRIMARY KEY,status VARCHAR(32) NOT NULL,created_at DATETIME NOT NULL);
CREATE TABLE sales_order_items(so_id VARCHAR(32),sku VARCHAR(32),qty INT NOT NULL,PRIMARY KEY(so_id,sku),FOREIGN KEY(so_id) REFERENCES sales_orders(so_id),FOREIGN KEY(sku) REFERENCES products(sku));
CREATE TABLE inventory(sku VARCHAR(32) PRIMARY KEY,stock_qty INT NOT NULL,updated_at DATETIME NOT NULL,FOREIGN KEY(sku) REFERENCES products(sku));
CREATE TABLE stock_movements(movement_id BIGINT AUTO_INCREMENT PRIMARY KEY,source_type VARCHAR(32) NOT NULL,source_id VARCHAR(32) NOT NULL,sku VARCHAR(32) NOT NULL,qty_delta INT NOT NULL,stock_before INT NOT NULL,stock_after INT NOT NULL,occurred_at DATETIME NOT NULL,INDEX idx_source(source_id,source_type),INDEX idx_sku_time(sku,occurred_at),FOREIGN KEY(sku) REFERENCES products(sku));
