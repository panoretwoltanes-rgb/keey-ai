"""AI 需求解析服务 - 第一版：结构化模拟解析"""
import re
from services.ai_order_schema import empty_ai_order, empty_ai_requirement

# 关键词 → 标准产品名映射（模拟 AI 识别）
_KEYWORD_MAP = {
    "柔光三代": "QY-TH09055S",
    "TH09055": "QY-TH09055S",
    "09055": "QY-TH09055S",
    "射灯": None,
    "筒灯": None,
    "磁吸灯": None,
    "灯带": None,
    "洗墙灯": None,
}

# 房间/空间关键词
_SPACES = ["客厅", "卧室", "主卧", "次卧", "书房", "餐厅", "厨房",
           "卫生间", "阳台", "过道", "玄关", "走廊", "楼梯"]

# 颜色
_COLORS = ["白色", "黑色", "镍色", "金色", "银色", "白+白", "白+黑"]

# 色温
_CCTS = ["3000K", "4000K", "3500K", "2700K", "6000K"]

# 光束角
_BEAMS = ["15°", "24°", "36°", "50°"]


def _find_space(text: str) -> str:
    for s in sorted(_SPACES, key=len, reverse=True):
        if s in text:
            return s
    return ""


def _find_keyword(text: str) -> str:
    """从文本中提取产品关键词。"""
    for kw in sorted(_KEYWORD_MAP.keys(), key=len, reverse=True):
        if kw in text:
            return kw
    return ""


def _find_power(text: str) -> str:
    m = re.search(r"(\d+)\s*W", text)
    return m.group(0) if m else ""


def _find_color(text: str) -> str:
    for c in _COLORS:
        if c in text:
            return c
    return ""


def _find_cct(text: str) -> str:
    for c in _CCTS:
        if c in text:
            return c
    return ""


def _find_beam(text: str) -> str:
    for b in _BEAMS:
        if b in text:
            return b
    return ""


def _find_quantity(text: str) -> tuple:
    """返回 (去除数量后的文本, 数量值, 单位)"""
    m = re.search(r"(\d+)\s*([个只盏套米条根台])", text)
    if m:
        return m.group(0), int(m.group(1)), m.group(2)
    m = re.search(r"(\d+)$", text)
    if m:
        return m.group(0), int(m.group(1)), "个"
    return "", 0, ""


def parse_customer_text(text: str) -> dict:
    """解析客户自然语言，返回 AI 需求订单。"""
    result = empty_ai_order()

    # 尝试提取客户名（"xxx，"或"xxx，"开头的部分）
    m = re.match(r"^([^，,]+)[，,]", text)
    if m:
        result["customer"] = m.group(1).strip()
        text = text[m.end():]

    # 尝试提取项目名（"xxx，"第二部分）
    m = re.match(r"^([^，,]+)[，,]", text)
    if m:
        result["project"] = m.group(1).strip()
        text = text[m.end():]

    # 按 "，" 分隔各需求
    segments = re.split(r"[，,;；]", text)

    for seg in segments:
        seg = seg.strip()
        if not seg:
            continue

        req = empty_ai_requirement()
        req["space"] = _find_space(seg)
        req["keyword"] = _find_keyword(seg)
        req["power"] = _find_power(seg)
        req["color"] = _find_color(seg)
        req["cct"] = _find_cct(seg)
        req["beam"] = _find_beam(seg)
        _, qty, unit = _find_quantity(seg)
        req["quantity"] = qty
        req["unit"] = unit

        if req["keyword"] or req["quantity"] > 0:
            result["requirements"].append(req)

    return result