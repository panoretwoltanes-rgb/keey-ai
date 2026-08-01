"""订单构建服务 - AI需求 → 标准报价订单"""
from services.quote_schema import empty_order
from services.product_matcher_service import match_requirement
from services.pricing_service import calculate_total
from services.discount_service import apply_discount


def build_quote_order(ai_order: dict) -> dict:
    """AI需求订单 → 标准报价订单。

    输入: ai_parser_service 输出的 AI 需求格式
    输出: quote_schema 标准订单格式
    """
    order = empty_order()
    order["customer"] = ai_order.get("customer", "")
    order["project"] = ai_order.get("project", "")

    errors = []

    for req in ai_order.get("requirements", []):
        result = match_requirement(req)
        if not result.get("success"):
            kw = req.get("keyword", "未知")
            errors.append(f"未找到匹配产品：{kw}")
            continue

        order["products"].append({
            "model": result.get("model", ""),
            "name": result.get("name", ""),
            "color": result.get("color", ""),
            "cct": req.get("cct", ""),
            "beam": req.get("beam", ""),
            "quantity": result.get("quantity", 0),
            "unit_price": result.get("unit_price", 0),
            "total_price": result.get("unit_price", 0) * result.get("quantity", 0),
        })

    if errors:
        return {"success": False, "message": "\n".join(errors), "data": None}

    if not order["products"]:
        return {"success": False, "message": "未识别到任何产品", "data": None}

    # 计算
    calculate_total(order)
    apply_discount(order)

    return {"success": True, "message": "ok", "data": order}