"""标准报价数据结构"""
def empty_order() -> dict:
    return {"customer": "", "project": "", "products": []}

def empty_product() -> dict:
    return {
        "model": "",
        "name": "",
        "color": "",
        "cct": "",
        "beam": "",
        "quantity": 0,
        "unit_price": 0,
        "total_price": 0
    }

def validate_order(data: dict) -> list:
    errors = []
    if not data.get("customer"):
        errors.append("缺少客户")
    if not data.get("products"):
        errors.append("缺少产品")
    for i, p in enumerate(data.get("products", [])):
        if not p.get("model"):
            errors.append(f"产品{i+1}缺少型号")
        if not p.get("quantity", 0) > 0:
            errors.append(f"产品{i+1}数量无效")
        if not p.get("unit_price", 0) > 0:
            errors.append(f"产品{i+1}未匹配到价格")
    return errors