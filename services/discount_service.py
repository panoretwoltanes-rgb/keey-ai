"""折扣计算服务"""

def apply_discount(order: dict, discount: float = 1.0) -> dict:
    """应用折扣。

    参数:
        discount: 折扣率，1.0 = 无折扣，0.9 = 九折

    返回:
        order 增加 discount / original_amount / final_amount 字段
    """
    total = order.get("total_amount", 0)
    order["original_amount"] = total
    order["discount"] = discount
    order["final_amount"] = round(total * discount, 2)
    return order