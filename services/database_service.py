"""SQLite 数据库服务"""
import os, sqlite3, time
from flask import current_app
from config import OUTPUT_DIR

_DB = os.path.join(OUTPUT_DIR, "quote.db")

def _get_conn():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    conn = sqlite3.connect(_DB)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = _get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer TEXT NOT NULL,
            project TEXT DEFAULT '',
            filename TEXT NOT NULL,
            total_amount REAL DEFAULT 0,
            discount REAL DEFAULT 1.0,
            final_amount REAL DEFAULT 0,
            create_time TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            model TEXT NOT NULL,
            name TEXT DEFAULT '',
            color TEXT DEFAULT '',
            quantity INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0,
            total_price REAL DEFAULT 0,
            FOREIGN KEY (order_id) REFERENCES orders(id)
        );
    """)
    conn.commit()
    conn.close()

def save_order(order: dict, filename: str):
    conn = _get_conn()
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO orders (customer, project, filename, total_amount, discount, final_amount, create_time) VALUES (?,?,?,?,?,?,?)",
        (order.get("customer", ""), order.get("project", ""), filename,
         order.get("total_amount", 0), order.get("discount", 1.0),
         order.get("final_amount", 0), now)
    )
    order_id = cur.lastrowid
    for p in order.get("products", []):
        conn.execute(
            "INSERT INTO order_items (order_id, model, name, color, quantity, unit_price, total_price) VALUES (?,?,?,?,?,?,?)",
            (order_id, p.get("model", ""), p.get("name", ""), p.get("color", ""),
             p.get("quantity", 0), p.get("unit_price", 0), p.get("total_price", 0))
        )
    conn.commit()
    conn.close()

def get_recent(limit: int = 10) -> list:
    conn = _get_conn()
    rows = conn.execute(
        "SELECT * FROM orders ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_order_detail(order_id: int) -> dict:
    conn = _get_conn()
    order = conn.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
    if not order:
        conn.close()
        return {}
    items = conn.execute("SELECT * FROM order_items WHERE order_id=?", (order_id,)).fetchall()
    conn.close()
    result = dict(order)
    result["items"] = [dict(i) for i in items]
    return result

get_all_detail = get_order_detail


