"""产品分类服务 - 客户叫法 → V1 产品库分类"""
import sys, os, json

_CAT_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "product_category_map.json")

def _load_categories() -> dict:
    try:
        with open(_CAT_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
            return {k: v for k, v in data.items() if not k.startswith("_")}
    except Exception as e:
        print(f"[分类] 加载失败: {e}")
        return {}

def match_category(keyword: str) -> dict:
    """客户叫法 → 最匹配的分类。"""
    cats = _load_categories()
    if not keyword:
        return {}
    
    # 精确匹配别名
    for cat_name, cat_data in cats.items():
        for alias in cat_data.get("aliases", []):
            if keyword == alias or alias in keyword or keyword in alias:
                return {"category": cat_name, "sheets": cat_data.get("sheets", []), "keywords": cat_data.get("keywords", [])}
    
    # 关键词匹配
    for cat_name, cat_data in cats.items():
        for kw in cat_data.get("keywords", []):
            if kw in keyword or keyword in kw:
                return {"category": cat_name, "sheets": cat_data.get("sheets", []), "keywords": cat_data.get("keywords", [])}
    
    return {}

def expand_keywords(keyword: str) -> list:
    """扩展客户关键词 → 搜索关键词列表（含分类扩展）。"""
    cat = match_category(keyword)
    if not cat:
        return [keyword]
    result = [keyword] + cat.get("keywords", [])
    return list(set(result))