from __future__ import annotations
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from .config import DB_PATH

SCHEMA = r'''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS products (
  sku TEXT PRIMARY KEY,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL,
  safety_stock INTEGER NOT NULL CHECK(safety_stock >= 0)
);
CREATE TABLE IF NOT EXISTS suppliers (
  supplier_id TEXT PRIMARY KEY,
  supplier_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS purchase_orders (
  po_id TEXT PRIMARY KEY,
  supplier_id TEXT NOT NULL REFERENCES suppliers(supplier_id),
  status TEXT NOT NULL CHECK(status IN ('PENDING_RECEIPT','PARTIAL_RECEIVED','RECEIVED','CANCELLED')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS purchase_order_items (
  po_id TEXT NOT NULL REFERENCES purchase_orders(po_id),
  sku TEXT NOT NULL REFERENCES products(sku),
  ordered_qty INTEGER NOT NULL CHECK(ordered_qty > 0),
  received_qty INTEGER NOT NULL DEFAULT 0 CHECK(received_qty >= 0),
  PRIMARY KEY(po_id, sku),
  CHECK(received_qty <= ordered_qty)
);
CREATE TABLE IF NOT EXISTS sales_orders (
  so_id TEXT PRIMARY KEY,
  status TEXT NOT NULL CHECK(status IN ('PENDING','BLOCKED_STOCK','READY_TO_SHIP','SHIPPED','CANCELLED')),
  created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sales_order_items (
  so_id TEXT NOT NULL REFERENCES sales_orders(so_id),
  sku TEXT NOT NULL REFERENCES products(sku),
  qty INTEGER NOT NULL CHECK(qty > 0),
  PRIMARY KEY(so_id, sku)
);
CREATE TABLE IF NOT EXISTS inventory (
  sku TEXT PRIMARY KEY REFERENCES products(sku),
  stock_qty INTEGER NOT NULL CHECK(stock_qty >= 0),
  updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS stock_movements (
  movement_id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_type TEXT NOT NULL CHECK(source_type IN ('PURCHASE_RECEIPT','SALES_SHIPMENT','ADJUSTMENT')),
  source_id TEXT NOT NULL,
  sku TEXT NOT NULL REFERENCES products(sku),
  qty_delta INTEGER NOT NULL,
  stock_before INTEGER NOT NULL,
  stock_after INTEGER NOT NULL,
  occurred_at TEXT NOT NULL,
  CHECK(stock_after = stock_before + qty_delta),
  CHECK(stock_after >= 0)
);
CREATE INDEX IF NOT EXISTS idx_movement_source ON stock_movements(source_id, source_type);
CREATE INDEX IF NOT EXISTS idx_movement_sku_time ON stock_movements(sku, occurred_at DESC);
'''

SEED = [
("products", ("SKU001", "P2000 Series Laser Printer", "Printer", 2)),
("products", ("SKU002", "T200 Toner Cartridge", "Consumable", 5)),
("products", ("SKU003", "M600 Label Printer", "Printer", 1)),
("suppliers", ("SUP01", "华南打印设备供应商")),
("suppliers", ("SUP02", "耗材合作供应商")),
("purchase_orders", ("PO100", "SUP01", "PARTIAL_RECEIVED", "2026-09-28 09:00:00")),
("purchase_orders", ("PO101", "SUP02", "RECEIVED", "2026-09-27 10:30:00")),
("purchase_orders", ("PO102", "SUP01", "PENDING_RECEIPT", "2026-09-30 15:20:00")),
("purchase_order_items", ("PO100", "SKU001", 5, 3)),
("purchase_order_items", ("PO101", "SKU002", 20, 20)),
("purchase_order_items", ("PO102", "SKU003", 4, 0)),
("sales_orders", ("SO100", "BLOCKED_STOCK", "2026-10-01 08:30:00")),
("sales_orders", ("SO101", "SHIPPED", "2026-09-30 14:00:00")),
("sales_orders", ("SO102", "READY_TO_SHIP", "2026-10-01 10:15:00")),
("sales_order_items", ("SO100", "SKU001", 5)),
("sales_order_items", ("SO101", "SKU002", 4)),
("sales_order_items", ("SO102", "SKU002", 3)),
("inventory", ("SKU001", 3, "2026-10-01 08:00:00")),
("inventory", ("SKU002", 16, "2026-09-30 14:05:00")),
("inventory", ("SKU003", 0, "2026-10-01 08:00:00")),
("stock_movements", ("PURCHASE_RECEIPT", "PO100", "SKU001", 3, 0, 3, "2026-09-29 11:00:00")),
("stock_movements", ("PURCHASE_RECEIPT", "PO101", "SKU002", 20, 0, 20, "2026-09-28 16:00:00")),
("stock_movements", ("SALES_SHIPMENT", "SO101", "SKU002", -4, 20, 16, "2026-09-30 14:05:00")),
]

INSERT_SQL = {
"products":"INSERT INTO products(sku,product_name,category,safety_stock) VALUES (?,?,?,?)",
"suppliers":"INSERT INTO suppliers(supplier_id,supplier_name) VALUES (?,?)",
"purchase_orders":"INSERT INTO purchase_orders(po_id,supplier_id,status,created_at) VALUES (?,?,?,?)",
"purchase_order_items":"INSERT INTO purchase_order_items(po_id,sku,ordered_qty,received_qty) VALUES (?,?,?,?)",
"sales_orders":"INSERT INTO sales_orders(so_id,status,created_at) VALUES (?,?,?)",
"sales_order_items":"INSERT INTO sales_order_items(so_id,sku,qty) VALUES (?,?,?)",
"inventory":"INSERT INTO inventory(sku,stock_qty,updated_at) VALUES (?,?,?)",
"stock_movements":"INSERT INTO stock_movements(source_type,source_id,sku,qty_delta,stock_before,stock_after,occurred_at) VALUES (?,?,?,?,?,?,?)",
}

@contextmanager
def connect(db_path: str | Path = DB_PATH):
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
    finally:
        conn.close()

def rebuild_demo_db(db_path: str | Path = DB_PATH) -> Path:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists(): path.unlink()
    with connect(path) as conn:
        conn.executescript(SCHEMA)
        for table, values in SEED:
            conn.execute(INSERT_SQL[table], values)
        conn.commit()
    return path
