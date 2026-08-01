"""产品查询服务 - 统一调用 V1 产品数据库"""
import sys, os, importlib.util

_V1_SCRIPTS = r"E:\新建文件夹 (2)\灯具报价\KEEY报价助手_V1.0_Stable_RESTORE\scripts"

def _get_v1_resolver():
    """获取 V1 的 resolve_products 函数。"""
    _old_path = sys.path.copy()
    _stdlib = [p for p in sys.path if p.lower().startswith(os.path.dirname(os.__file__).lower())]
    sys.path = _stdlib + [_V1_SCRIPTS]
    for n in list(sys.modules.keys()):
        if n in ("config", "product_resolver"):
            del sys.modules[n]
    spec = importlib.util.spec_from_file_location("v1_resolver",
        os.path.join(_V1_SCRIPTS, "product_resolver.py"))
    mod = importlib.util.module_from_spec(spec)
    old_cwd = os.getcwd()
    os.chdir(_V1_SCRIPTS)
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(old_cwd)
    sys.path = _old_path
    return mod.resolve_products

_resolve = _get_v1_resolver()


def lookup(model: str, color: str = "") -> dict:
    """从 V1 产品数据库查询产品，返回 {"model","name","color","price","unit","params","hole"}"""
    keyword = model
    if color and color not in keyword:
        keyword = f"{model} {color}"
    results = _resolve([{"型号": keyword, "数量": 1}])
    if results:
        r = results[0]
        return {
            "model": r.get("型号", model),
            "name": r.get("型号", ""),
            "color": color,
            "price": r.get("单价", 0),
            "unit": r.get("单位", ""),
            "params": r.get("参数", ""),
            "hole": r.get("开孔", ""),
        }
    return {"model": model, "name": "", "color": color, "price": 0, "unit": "", "params": "", "hole": ""}


def enrich_order(order: dict) -> dict:
    """为订单中每个产品补充产品库信息。"""
    for p in order.get("products", []):
        info = lookup(p.get("model", ""), p.get("color", ""))
        # 已有型号名时不覆盖（NLP 路径已设置正确名称）
        if not p.get("name"):
            p["name"] = info.get("name", "")
        # 已有价格时不覆盖（NLP 路径已设置正确单价）
        existing = p.get("unit_price", 0)
        p["price"] = existing if existing > 0 else info.get("price", 0)
        p["unit"] = info.get("unit", p.get("unit", ""))
    return order
