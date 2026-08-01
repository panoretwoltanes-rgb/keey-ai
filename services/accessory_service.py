"""配件服务 - 根据产品库参数自动追加配件"""
import re, json, os


def _load_rules() -> dict:
    """从配置文件加载配件规则。"""
    path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "product_keyword_rules.json")
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data.get("accessory", {})
    except:
        return {}


def _get_trigger_patterns() -> list:
    """从配置读取触发关键词列表。"""
    rules = _load_rules()
    return rules.get("trigger_patterns", ["预埋", "无边框"])


def _get_model_regex() -> str:
    """从配置读取型号提取正则。"""
    rules = _load_rules()
    me = rules.get("model_extract", {})
    return me.get("regex", r"(?:QY-)?[A-Z]{2,3}\d{2,}[A-Za-z0-9\-]*")


def needs_accessory(params_text: str) -> bool:
    """根据产品参数判断是否需要自动追加配件。
    
    判断逻辑完全由配置文件 data/product_keyword_rules.json 的 accessory.trigger_patterns 控制。
    后续产品库新增描述时，只需修改 JSON，无需改代码。
    """
    if not params_text:
        return False
    text = params_text.lower()
    patterns = _get_trigger_patterns()
    for p in patterns:
        if p.lower() in text:
            return True
    return False


def extract_model_numbers(text: str) -> list:
    """从文本中提取可能的型号标识。
    
    正则从配置文件 data/product_keyword_rules.json 的 accessory.model_extract.regex 读取。
    """
    if not text:
        return []
    regex = _get_model_regex()
    models = []
    for m in re.findall(regex, text):
        m = m.strip().strip("-/")
        if m and len(m) >= 5 and m not in models:
            models.append(m)
    return models


def lookup_product(model_keyword: str) -> dict:
    """在产品库中搜索产品。"""
    from services.product_lookup_service import exact_db_lookup
    return exact_db_lookup(model_keyword) or None


def is_accessory_product(product: dict) -> bool:
    """判断产品是否为配件类别。
    
    判定规则完全由配置文件 data/product_keyword_rules.json 的 accessory.identify_rules.rules 控制。
    新增配件类型时只需修改 JSON，无需改代码。
    """
    if not product:
        return False
    rules = _load_rules()
    identify = rules.get("identify_rules", {})
    for rule in identify.get("rules", []):
        field = rule.get("field", "")
        contains = rule.get("contains", "")
        startswith = rule.get("startswith", "")
        val = (product.get(field, "") or "").strip()
        if contains and contains in val:
            return True
        if startswith and val.startswith(startswith):
            return True
    return False


def _convert_model_for_accessory(model: str) -> str:
    """配件查询时的型号清理：去掉颜色后缀，TH 转 WB。"""
    if not model:
        return model
    base = model.split(maxsplit=1)[0]
    if base.startswith("QY-TH"):
        base = base.replace("QY-TH", "QY-WB", 1)
        print(f"[配件] 型号转换: {model} -> {base}")
        return base
    if base.startswith("QY-WB"):
        print(f"[配件] 型号转换: {model} -> {base}")
        return base
    return model


def get_accessories_for_product_model(model: str, force: bool = False) -> list:
    """根据产品型号查库 → 读参数 → 判断是否需要配件 → 提取型号 → 验证 → 返回。
    
    Args:
        model: 产品型号
        force: 为 True 时跳过 needs_accessory() 检查，直接解析配件
    """
    print(f"[配件] 原始型号: {model}")
    cleaned = _convert_model_for_accessory(model)
    print(f"[配件] force_wb清理后型号: {cleaned}")
    from services.product_lookup_service import exact_db_lookup
    print(f"[配件诊断] lookup_model={cleaned}")
    record = exact_db_lookup(cleaned)
    if not record:
        print(f"[配件] 精确查库未找到: {cleaned}")
        return []
    params_text = record.get("参数", "") or ""
    matched_name = record.get("型号", "") or ""
    print(f"\n[配件] 产品: {matched_name}")
    print(f"[配件] 参数: {params_text[:120]}...")
    print(f"[配件诊断] params_length={len(params_text)}")
    if not params_text:
        print("[配件] 参数为空，跳过")
        return []
    if not force and not needs_accessory(params_text):
        print("[配件] 参数无需配件，跳过")
        return []

    # 预埋盒 mapping 优先：固定映射表 > 参数提取
    if force:
        try:
            mapping_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "accessory_mapping.json")
            with open(mapping_path, "r", encoding="utf-8-sig") as _f:
                mapping_cfg = json.load(_f)
            wb_to_zh = mapping_cfg.get("wb_to_zh", {})
            base_key = cleaned.split()[0]
            zh_model = wb_to_zh.get(base_key, "")
            # 兼容 K2 变体：QY-WB06055S-K2 → QY-WB06055S
            if not zh_model and "-K2" in base_key:
                zh_model = wb_to_zh.get(base_key.replace("-K2", ""), "")
            print(f"[预埋兜底] 映射表: {base_key} -> {zh_model or '未配置'}")
            if zh_model:
                info = lookup_product(zh_model)
                if info and is_accessory_product(info):
                    print(f"[配件] √ 确认(mapping): {info.get('型号','')}  @{info.get('单价',0)}/{info.get('单位','')}")
                    return [info]
        except Exception as e:
            print(f"[预埋兜底] 映射查询失败: {e}")

    if force:
        print("[配件] 订单指令强制追加，提取配件型号...")
    else:
        print("[配件] 参数含触发关键词，提取配件型号...")
    all_models = extract_model_numbers(params_text)
    print(f"[配件] 提取到型号: {all_models}")
    print(f"[配件诊断] 提取数={len(all_models)}")
    results = []
    seen = set()
    for cm in all_models:
        print(f"[配件诊断] 验证: {cm}")
        if cm in seen:
            continue
        seen.add(cm)
        info = lookup_product(cm)
        print(f"[配件诊断] lookup_product({cm}) -> {bool(info)}")
        if info and is_accessory_product(info):
            am = (info.get("型号", "") or "").strip()
            if am and am not in {r.get("型号", "") for r in results}:
                results.append(info)
                print(f"[配件] √ 确认: {am}  @{info.get('单价',0)}/{info.get('单位','')}")
        elif info:
            print(f"[配件] × 非配件: {cm} → {info.get('型号','')}")
        else:
            print(f"[配件] × 未找到: {cm}")
    print(f"[配件诊断] 返回配件数={len(results)}")
    # 预埋兜底：参数中无适配引用时，使用映射表
    if not results and force:
        print("[预埋兜底] 参数无适配引用，查询映射表...")
        print(f"[预埋兜底] 原型号: {model}")
        print(f"[预埋兜底] 清理型号: {cleaned}")
        try:
            mapping_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "accessory_mapping.json")
            with open(mapping_path, "r", encoding="utf-8-sig") as _f:
                mapping_cfg = json.load(_f)
            wb_to_zh = mapping_cfg.get("wb_to_zh", {})
            # 匹配清理后的基础型号（去掉颜色后缀）
            base_key = cleaned.split()[0]
            zh_model = wb_to_zh.get(base_key, "")
            print(f"[预埋兜底] 匹配规则: {base_key} -> {zh_model or '未找到'}")
            if zh_model:
                info = lookup_product(zh_model)
                print(f"[预埋兜底] 返回预埋盒: {zh_model}")
                if info and is_accessory_product(info):
                    results.append(info)
                    print(f"[配件] √ 确认(兜底): {info.get('型号','')}  @{info.get('单价',0)}/{info.get('单位','')}")
        except Exception as e:
            print(f"[预埋兜底] 映射查询失败: {e}")
    return results
