from __future__ import annotations
from .db import connect
from .config import DB_PATH

class ERPDataNotFound(KeyError):
    pass

SQL_CATALOG={
    'get_stock':{
        'purpose':'按SKU查询商品、当前库存与安全库存，用于库存事实查询和低库存判断。',
        'tables':['products','inventory'],
        'join':'products.sku = inventory.sku',
        'sql':'''SELECT p.sku,p.product_name,p.category,i.stock_qty,p.safety_stock,\nCASE WHEN i.stock_qty < p.safety_stock THEN 1 ELSE 0 END AS below_safety_stock,i.updated_at\nFROM products p JOIN inventory i ON i.sku=p.sku WHERE p.sku=?'''
    },
    'get_purchase_order':{
        'purpose':'按采购订单查询供应商、SKU、采购量、累计验收量与剩余量。',
        'tables':['purchase_orders','suppliers','purchase_order_items','products'],
        'join':'PO→supplier；PO→item；item→product',
        'sql':'''SELECT po.po_id,po.status,po.created_at,s.supplier_name,poi.sku,p.product_name,poi.ordered_qty,poi.received_qty,(poi.ordered_qty-poi.received_qty) AS remaining_qty\nFROM purchase_orders po JOIN suppliers s ON s.supplier_id=po.supplier_id JOIN purchase_order_items poi ON poi.po_id=po.po_id JOIN products p ON p.sku=poi.sku WHERE po.po_id=?'''
    },
    'get_sales_order':{
        'purpose':'按销售订单查询SKU、订单数量、当前库存与假设出库后库存。',
        'tables':['sales_orders','sales_order_items','products','inventory'],
        'join':'SO→item→product/inventory',
        'sql':'''SELECT so.so_id,so.status,so.created_at,soi.sku,p.product_name,soi.qty,i.stock_qty,(i.stock_qty-soi.qty) AS stock_after_if_shipped\nFROM sales_orders so JOIN sales_order_items soi ON soi.so_id=so.so_id JOIN products p ON p.sku=soi.sku JOIN inventory i ON i.sku=soi.sku WHERE so.so_id=?'''
    },
    'recent_movements':{
        'purpose':'查询SKU最近库存流水，解释库存“为什么变成现在这样”。',
        'tables':['stock_movements'],
        'join':'无',
        'sql':'''SELECT source_type,source_id,sku,qty_delta,stock_before,stock_after,occurred_at\nFROM stock_movements WHERE sku=? ORDER BY occurred_at DESC,movement_id DESC LIMIT ?'''
    },
    'movements_by_source':{
        'purpose':'按PO/SO来源单据追溯对应库存流水。',
        'tables':['stock_movements'],
        'join':'无',
        'sql':'''SELECT source_type,source_id,sku,qty_delta,stock_before,stock_after,occurred_at\nFROM stock_movements WHERE source_id=? ORDER BY movement_id'''
    },
    'stock_summary':{
        'purpose':'汇总所有SKU库存并按安全库存标记库存健康状态。',
        'tables':['products','inventory'],
        'join':'products.sku = inventory.sku',
        'sql':'''SELECT p.sku,p.product_name,i.stock_qty,p.safety_stock,CASE WHEN i.stock_qty < p.safety_stock THEN 'LOW' ELSE 'OK' END AS stock_health\nFROM products p JOIN inventory i ON i.sku=p.sku ORDER BY p.sku'''
    }
}

def explain_tool(name:str,params:dict|None=None):
    item=SQL_CATALOG[name]
    return {"tool":name,"purpose":item['purpose'],"tables":item['tables'],"join":item['join'],"params":params or {}}

def _one(sql, params=(), db_path=DB_PATH):
    with connect(db_path) as conn:
        row = conn.execute(sql, params).fetchone()
    if row is None:
        raise ERPDataNotFound(params[0] if params else "record")
    return dict(row)

def get_stock(sku: str, db_path=DB_PATH):
    return _one(SQL_CATALOG['get_stock']['sql'], (sku.upper(),), db_path)

def get_purchase_order(po_id: str, db_path=DB_PATH):
    return _one(SQL_CATALOG['get_purchase_order']['sql'], (po_id.upper(),), db_path)

def get_sales_order(so_id: str, db_path=DB_PATH):
    return _one(SQL_CATALOG['get_sales_order']['sql'], (so_id.upper(),), db_path)

def recent_movements(sku: str, limit: int = 5, db_path=DB_PATH):
    limit=max(1,min(int(limit),20))
    with connect(db_path) as conn:
        rows=conn.execute(SQL_CATALOG['recent_movements']['sql'],(sku.upper(),limit)).fetchall()
    return [dict(r) for r in rows]

def movements_by_source(source_id: str, db_path=DB_PATH):
    with connect(db_path) as conn:
        rows=conn.execute(SQL_CATALOG['movements_by_source']['sql'],(source_id.upper(),)).fetchall()
    return [dict(r) for r in rows]

def stock_summary(db_path=DB_PATH):
    with connect(db_path) as conn:
        rows=conn.execute(SQL_CATALOG['stock_summary']['sql']).fetchall()
    return [dict(r) for r in rows]
