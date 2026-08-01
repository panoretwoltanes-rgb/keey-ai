"""产品匹配服务 - AI需求 → 正式产品库匹配"""
import sys, os, json
import importlib.util
from services.product_category_service import expand_keywords

_V1_SCRIPTS = r"E:\新建文件夹 (2)\灯具报价\KEEY报价助手_V1.0_Stable_RESTORE\scripts"
_ALIAS_PATH = r"E:\新建文件夹 (2)\灯具报价\KEEY_AI_Quote\data\product_alias.json"

_COLOR_MAP = {
    "白色": "白+白", "黑色": "黑+黑", "镍色": "白+镍",
    "金色": "金", "银色": "银", "白+白": "白+白",
    "白+黑": "白+黑", "黑+黑": "黑+黑",
}


def _load_aliases() -> dict:
    try:
        with open(_ALIAS_PATH, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"[alias] 文件格式错误: 期望dict, 实际{type(data)}")
            return {}
        aliases = {k: v for k, v in data.items() if not k.startswith("_")}
        print(f"[alias] JSON总键数: {len(data)}, 映射数: {len(aliases)}")
        return aliases
    except Exception as e:
        print(f"[alias] 加载失败: {e}")
        return {}

def _resolve_alias(keyword: str, aliases: dict) -> list:
    """客户叫法 → 正式搜索关键词列表（支持多关键词）。"""
    if not keyword:
        return [keyword]
    # 精确匹配
    if keyword in aliases:
        val = aliases[keyword]
        if isinstance(val, list):
            return val
        return [val]
    # 前缀匹配
    for k, v in sorted(aliases.items(), key=lambda x: -len(x[0])):
        if k in keyword:
            if isinstance(v, list):
                return v
            return [v]
    return [keyword]

def _get_v1_resolver():
    _old_path = sys.path.copy()
    _stdlib = [p for p in sys.path if p.lower().startswith(os.path.dirname(os.__file__).lower())]
    sys.path = _stdlib + [_V1_SCRIPTS]

    # 预加载 V1 config，防止被 V2 config 覆盖
    for n in list(sys.modules.keys()):
        if n in ("config", "product_resolver"):
            del sys.modules[n]

    v1_config_spec = importlib.util.spec_from_file_location(
        "v1_config",
        os.path.join(_V1_SCRIPTS, "config.py")
    )
    v1_config_mod = importlib.util.module_from_spec(v1_config_spec)
    old_cwd = os.getcwd()
    os.chdir(_V1_SCRIPTS)
    try:
        v1_config_spec.loader.exec_module(v1_config_mod)
    finally:
        os.chdir(old_cwd)
    sys.modules["config"] = v1_config_mod

    # 加载 V1 product_resolver
    spec = importlib.util.spec_from_file_location(
        "v1_resolver",
        os.path.join(_V1_SCRIPTS, "product_resolver.py")
    )
    mod = importlib.util.module_from_spec(spec)
    os.chdir(_V1_SCRIPTS)
    try:
        spec.loader.exec_module(mod)
    finally:
        os.chdir(old_cwd)
    sys.path = _old_path
    return mod.resolve_products

_resolve = _get_v1_resolver()

def match_requirement(req: dict) -> dict:
    """AI需求 → 正式产品匹配。"""
    keyword = req.get("keyword", "")
    color_input = req.get("color", "")
    quantity = req.get("quantity", 0)
    power = req.get("power", "")

    if not keyword:
        return {"success": False, "message": "缺少关键词"}

    aliases = _load_aliases()

    search_keys = _resolve_alias(keyword, aliases)
    print(f"[alias] 原始keyword: {keyword}")
    print(f"[alias] 转换后: {search_keys}")

    # 分类扩展
    from services.product_category_service import expand_keywords as expand_category_keywords
    category_keys = expand_category_keywords(keyword)
    search_keys = list(dict.fromkeys(search_keys + category_keys))
    print(f"[分类] 扩展后: {search_keys}")

    matched_color = _COLOR_MAP.get(color_input, color_input)
    all_results = []

    for sk in search_keys:
        full_key = sk
        if matched_color and matched_color not in full_key:
            full_key = f"{sk} {matched_color}"
        print(f"[搜索] 关键词: {full_key}")
        results = _resolve([{"型号": full_key, "数量": quantity or 1}])
        if results:
            all_results.extend(results)

    seen = set()
    unique = []
    for r in all_results:
        m = r.get("型号", "")
        if m not in seen:
            seen.add(m)
            unique.append(r)

    print(f"[V1搜索] 候选数量: {len(unique)}")

    # 收集所有候选（V1 + 数据库），统一评分过滤
    from services.product_database_search_service import search as db_search, score_product
    all_candidates = []

    # V1 结果评分
    for r in unique:
        scored = score_product(r, keyword)
        if scored.get("score", 0) > 0:
            all_candidates.append(scored)
            print(f"[评分] {scored.get('型号','')}  score={scored.get('score',0)}  ({scored.get('field','')})")

    # 数据库搜索（用所有扩展关键词）
    for db_kw in search_keys:
        db_results = db_search(db_kw)
        for dr in db_results:
            if dr.get("score", 0) > 0:
                all_candidates.append(dr)

    # 去重排序
    seen = set()
    final = []
    for c in sorted(all_candidates, key=lambda x: -x.get("score", 0)):
        m = c.get("型号", "")
        if m and m not in seen:
            seen.add(m)
            final.append(c)

    print(f"[搜索] 候选数量: {len(final)}")
    if final:
        best = final[0]
        print(f"[搜索] 选择: {best.get('型号', '')}  score={best.get('score', 0)}")
        return {
            "success": True,
            "model": best.get("型号", ""),
            "name": best.get("型号", ""),
            "color": matched_color,
            "quantity": quantity,
            "unit_price": best.get("单价", 0),
            "unit": best.get("单位", ""),
            "params": best.get("参数", ""),
            "hole": best.get("开孔", ""),
        }

    return {"success": False, "model": "", "unit_price": 0}
