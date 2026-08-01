"""报价业务层"""
from services.parser_service import parse_quote_text
from services.product_service import enrich_order
from services.pricing_service import calculate_total
from services.discount_service import apply_discount
from services.excel_service import generate_excel
from services.history_service import add_record
from services.database_service import init_db
import re, os
from services.product_text_parser import parse_product_text, build_order_from_parsed
from services.accessory_service import get_accessories_for_product_model
import json as _json


def _detect_accessory_directives(text: str) -> list:
    """检测用户输入中的订单级配件指令（如"都要预埋"）。
    
    配置完全由 data/accessory_directives.json 控制，新增指令只需改 JSON。
    """
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "data", "accessory_directives.json")
    try:
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            cfg = _json.load(f)
    except Exception as e:
        print(f"[配件指令] 加载配置失败: {e}")
        return []
    matched = []
    text_lower = text.lower()
    for d in cfg.get("directives", []):
        for p in d.get("patterns", []):
            if p.lower() in text_lower:
                matched.append(d["name"])
                print(f"[配件指令] 命中: \"{p}\" → 指令={d['name']}  handler={d.get('handler','')}")
                break
    return matched


def _extract_customer_project(text: str) -> tuple:
    """从文本中提取客户名称和项目名称。"""
    customer = ""
    project = ""
    for line in text.strip().split("\n"):
        line = line.strip()
        if "客户" in line and any(c in line for c in ["：", ":"]):
            for sep in ["：", ":"]:
                if sep in line:
                    customer = line.split(sep, 1)[-1].strip()
                    break
        elif "项目" in line and any(c in line for c in ["：", ":"]):
            for sep in ["：", ":"]:
                if sep in line:
                    project = line.split(sep, 1)[-1].strip()
                    break
    return customer, project


def _try_nlp_parse(text: str) -> dict:
    """尝试用自然语言解析器解析文本。"""
    parsed = parse_product_text(text)
    orders = parsed.get("订单", [])
    print(f"[NLP解析] parsed订单数: {len(orders)}")
    if orders:
        print(f"[NLP解析] parsed结构: 系列={parsed.get('系列','')} 颜色={parsed.get('颜色','')} 规格={parsed.get('规格','')}")
    else:
        print("[NLP解析] parsed结果: 无订单，进入回退")
        return None
    customer, project = _extract_customer_project(text)
    order = build_order_from_parsed(parsed)
    if customer:
        order["customer"] = customer
    if project:
        order["project"] = project
    print(f"[NLP订单] 产品数: {len(order.get('products',[]))}")
    if not order.get("products"):
        print("[NLP订单] 产品匹配无结果，进入回退")
        return None
    order["_nlp_install"] = parsed.get("安装", "")
    # 检测订单级配件指令
    order["_accessory_directives"] = _detect_accessory_directives(text)
    # 配件追加：统一在这里完成，任何调用方都拿到完整订单
    _try_auto_add_accessories(order)
    for p in order["products"]:
        print(f"  [NLP产品] {p.get('model','')}  {p.get('color','')}  {p.get('cct','')}  {p.get('beam','')}  x{p.get('quantity',0)}  @{p.get('unit_price',0)}")
    return order


def _try_auto_add_accessories(order: dict):
    """按产品追加配件：
    - 产品自身 pre_embedded=True（用户该行说了预埋）
    - 或产品系列 default_preinstall=true（如魔方）
    """
    default_preinstall_series = _get_default_preinstall_series()
    preembedded_series = set(default_preinstall_series)
    # 收集需要追加配件的产品
    targets = []
    for p in order.get("products", []):
        if p.get("_is_accessory"):
            continue
        p_series = p.get("_series_key", "")
        if p.get("pre_embedded") or p_series in preembedded_series:
            targets.append(p)
    if targets:
        print(f"[配件] 需追加配件产品: {[(p.get('model',''), p.get('quantity',0)) for p in targets]}")
        _add_preinstall_accessories(order, target_products=targets)
    else:
        print("[配件] 无产品需要追加配件")


def _get_default_preinstall_series() -> list:
    """读取配置中标记为默认预埋的系列名列表。"""
    cfg_path = os.path.join(os.path.dirname(__file__), "..", "data", "product_series.json")
    try:
        with open(cfg_path, "r", encoding="utf-8-sig") as f:
            cfg = _json.load(f)
        return [s.get("name", "") for s in cfg.get("series", []) if s.get("default_preinstall")]
    except:
        return []


def _add_preinstall_accessories(order: dict, only_series: list = None, target_products: list = None):
    """为订单中每款产品自动追加适配的预埋件。
    """
    print("======== AUTO ACCESSORY ========")
    pool = target_products if target_products is not None else order.get("products", [])
    extra_by_model = {}
    for p in pool:
        if p.get("_is_accessory"):
            continue
        if only_series:
            p_series = p.get("_series_key", "")
            if p_series not in only_series:
                continue
        model = p.get("model", "")
        qty = p.get("quantity", 0)
        print(f"product: {model}")
        print(f"directive: 预埋")
        print(f"params: {p.get('_db_record', {}).get('参数', '(未携带)')[:120]}")
        accs = get_accessories_for_product_model(model, force=True)
        print(f"matched accessory: {[a.get('型号','') for a in accs]}")
        for acc in accs:
            am = (acc.get("型号", "") or "").strip()
            if am:
                price = acc.get("单价", 0) or 0
                if am in extra_by_model:
                    extra_by_model[am]["quantity"] += qty
                    extra_by_model[am]["total_price"] = extra_by_model[am]["quantity"] * price
                else:
                    extra_by_model[am] = {
                        "model": am,
                        "name": am,
                        "color": "",
                        "cct": "",
                        "beam": "",
                        "quantity": qty,
                        "unit_price": price,
                        "total_price": price * qty,
                        "_is_accessory": True,
                    }
                print(f"  [预埋件] 追加: {am} x{qty}  @{price}")
    extra = list(extra_by_model.values())
    if extra:
        order["products"].extend(extra)
    print(f"accessories after: {len([x for x in order.get('products',[]) if x.get('_is_accessory')])}")
    print("[配件] 检查完成")
    print("===============================")


def _merge_duplicate_products(order: dict):
    """合并型号/参数/价格一致的产品行。"""
    merged = []
    index = {}
    for p in order.get("products", []):
        key = (
            p.get("model", ""),
            p.get("color", ""),
            p.get("unit_price", 0),
            p.get("cct", ""),
            p.get("beam", ""),
        )
        if key in index:
            target = index[key]
            target["quantity"] += p.get("quantity", 0)
            target["total_price"] = target["quantity"] * target.get("unit_price", 0)
            print(f"[合并] {target['model']} 数量合并: {target['quantity']}")
        else:
            index[key] = p
            merged.append(p)
    order["products"] = merged
    return order


def process_quote(text: str) -> dict:
    init_db()
    order = _try_nlp_parse(text)
    if order:
        print("[NLP解析] 成功")
    else:
        print("[NLP解析] 无结果，回退普通解析")
        order = parse_quote_text(text)

    enrich_order(order)
    calculate_total(order)
    _merge_duplicate_products(order)
    apply_discount(order)
    print("======== ORDER AFTER ENRICH ========")
    for _i, _p in enumerate(order.get("products", [])):
        print(f"  产品{_i+1}: {_json.dumps(_p, ensure_ascii=False)}")
    print(f"  total_amount={order.get('total_amount')}  final_amount={order.get('final_amount')}")
    print("====================================")

    print(f"客户: {order['customer']}")
    print(f"项目: {order['project']}")
    for p in order["products"]:
        print(f"  {p.get('model','')}  {p.get('name','')}  {p.get('unit_price',0)}x{p.get('quantity',0)}={p.get('total_price',0)}")
    print(f"  合计: {order.get('original_amount',0)}  折扣: {order.get('discount',1)}  应收: {order.get('final_amount',0)}")

    try:
        filename = generate_excel(order)
        add_record(order["customer"], order["project"], filename, order)
        return {
            "success": True,
            "message": "报价已生成",
            "data": {
                "customer": order.get("customer", ""),
                "project": order.get("project", ""),
                "total_amount": order.get("total_amount", 0),
                "final_amount": order.get("final_amount", 0),
                "products": [
                    {
                        "model": p.get("model", ""),
                        "quantity": p.get("quantity", 0),
                        "unit_price": p.get("unit_price", 0),
                        "total_price": p.get("total_price", 0)
                    }
                    for p in order.get("products", [])
                ]
            },
            "file": filename,
            "url": f"/download/{filename}"
        }
    except Exception as e:
        print(f"生成失败: {e}")
        return {"success": False, "message": str(e), "data": order}
