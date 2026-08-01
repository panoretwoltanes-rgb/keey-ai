"""历史报价服务 - SQLite 存储"""
from services.database_service import save_order, get_recent, get_all_detail

def add_record(customer: str, project: str, filename: str, order: dict = None):
    """保存报价记录。"""
    if order:
        save_order(order, filename)
    else:
        from services.database_service import _get_conn
        conn = _get_conn()
        import time
        conn.execute(
            "INSERT INTO orders (customer, project, filename, create_time) VALUES (?,?,?,?)",
            (customer, project, filename, time.strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        conn.close()

def get_all() -> list:
    return get_recent(999)

def get_recent_list(limit: int = 10) -> list:
    return get_recent(limit)