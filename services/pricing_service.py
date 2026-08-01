"""报价计算服务"""

def calculate_total(order: dict) -> dict:
    """计算每个产品的金额。"""
    for p in order.get("products", []):
        qty = p.get("quantity", 0)
        price = p.get("price", 0)
        p["unit_price"] = price
        p["total_price"] = price * qty
        # 清理临时字段
        if "price" in p:
            del p["price"]

    grand_total = sum(p.get("total_price", 0) for p in order.get("products", []))
    order["total_amount"] = grand_total
    return order