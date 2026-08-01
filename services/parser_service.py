"""报价文本解析服务 V2 - 支持自然语言输入"""
import re
from services.quote_schema import empty_order, empty_product

_COLORS = ["白+白", "白+黑", "白+镍", "黑+黑", "黑+白", "黑+镍",
           "白色", "黑色", "镍色", "金色", "银色", "砂白", "砂黑"]

_MODEL_PREFIX = r"(QY|GS|TH|DY|WB|ZH|DD|SJPX|S16)"

def _split_model_color(text: str):
    """将 "QY-TH09055S 白+白" 拆分为 ("QY-TH09055S", "白+白")"""
    for c in sorted(_COLORS, key=len, reverse=True):
        idx = text.find(c)
        if idx >= 0:
            model = text[:idx].strip()
            return model, c
    return text.strip(), ""

def _extract_qty(s: str):
    """从 "8个" 或 "8" 中提取数量。"""
    m = re.search(r"(\d+)(?:[个只盏套米条根台]|$)", s)
    if m:
        return int(m.group(1))
    return 0

def _has_model_pattern(s: str):
    return bool(re.search(_MODEL_PREFIX, s, re.IGNORECASE))

def _remove_qty_suffix(s: str):
    """去掉数量后缀，如 "8个" → "8" → 返回 ("clean", qty)"""
    qty = _extract_qty(s)
    if qty > 0:
        # 只删除末尾的数量（如 "2套"），不能删除行中第一个数字（如 "4000K" 中的 4000）
        s = re.sub(r"\d+[个只盏套米条根台]?\s*$", "", s, count=1).strip()
    return s, qty

def parse_quote_text(text: str) -> dict:
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    result = empty_order()
    result["raw"] = text.strip()
    if not lines:
        return result

    pending_model = ""
    found_product_area = False

    for s in lines:
        # 结构化字段
        if s.startswith("客户") and any(c in s for c in ["：", ":"]):
            for sep in ["：", ":"]:
                if sep in s:
                    result["customer"] = s.split(sep, 1)[-1].strip()
                    break
            continue

        if s.startswith("项目") and any(c in s for c in ["：", ":"]):
            for sep in ["：", ":"]:
                if sep in s:
                    result["project"] = s.split(sep, 1)[-1].strip()
                    break
            continue

        if s.startswith("产品") and any(c in s for c in ["：", ":"]):
            for sep in ["：", ":"]:
                if sep in s:
                    pending_model = s.split(sep, 1)[-1].strip()
                    found_product_area = True
                    break
            continue

        if s.startswith("数量") and any(c in s for c in ["：", ":"]) and pending_model:
            for sep in ["：", ":"]:
                if sep in s:
                    val = s.split(sep, 1)[-1].strip()
                    qty = _extract_qty(val)
                    if qty > 0:
                        model, color = _split_model_color(pending_model)
                        prod = empty_product()
                        prod["model"] = model
                        prod["color"] = color
                        prod["quantity"] = qty
                        result["products"].append(prod)
                        pending_model = ""
                    break
            continue

        # 检测型号+颜色+数量行
        content, qty = _remove_qty_suffix(s)
        if qty > 0 and _has_model_pattern(content):
            model, color = _split_model_color(content)
            prod = empty_product()
            prod["model"] = model
            prod["color"] = color
            prod["quantity"] = qty
            result["products"].append(prod)
            found_product_area = True
            continue

        # 无型号前缀但有数量（如 "灯带 8米"）
        if qty > 0 and not _has_model_pattern(content):
            model, color = _split_model_color(content)
            if model:
                prod = empty_product()
                prod["model"] = model
                prod["color"] = color
                prod["quantity"] = qty
                result["products"].append(prod)
                found_product_area = True
                continue

        # 自然行：非产品行作为项目名
        if not found_product_area:
            if not result["project"] and len(s) > 2:
                result["project"] = s

    return result
