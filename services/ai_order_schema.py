"""AI 需求订单数据结构"""

def empty_ai_order() -> dict:
    return {
        "customer": "",
        "project": "",
        "requirements": [],
    }

def empty_ai_requirement() -> dict:
    return {
        "keyword": "",
        "space": "",
        "power": "",
        "color": "",
        "cct": "",
        "beam": "",
        "quantity": 0,
        "unit": "",
    }