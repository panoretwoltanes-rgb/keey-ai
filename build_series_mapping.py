"""自动从产品库构建系列型号映射。

架构：
  1. 扫描产品库所有型号
  2. 提取基础型号（去掉 TH/WB/K2/颜色），统一归组
  3. 每组补齐 normal / normal_k2 / pre_embedded / pre_embedded_k2
  4. 每组建一次系列名（优先型号命名规律，最后用 E 列辅助）
  5. 自动更新 product_series.json
"""
import re, json, os, openpyxl
from collections import OrderedDict

DB_PATH = r"D:\0000AAA报价助手\1.2026企一产品报价表(最新）.xlsx"
SERIES_JSON = os.path.join("data", "product_series.json")

# 兜底系列关键词（仅当产品库完全无法识别系列时使用）
# 格式: [(关键词, 系列名)]
FALLBACK_SERIES_RULES = [
    ("柔光", "柔光"),
    ("明秀", "明秀"),
    ("魔方", "魔方"),
    ("焦点", "焦点"),
    ("银河", "银河"),
    ("星际", "星际"),
    ("敏行", "敏行"),
    ("暮光", "暮光"),
]

# E 列辅助系列关键词（从产品参数中识别）
SERIES_KEYWORDS = [
    "柔光", "明秀", "魔方", "焦点", "银河", "星际", "敏行", "暮光",
    "悦影", "悦幕", "紫同", "米家", "悦上", "悦明",
]


def parse_model_info(model: str) -> dict:
    """解析型号 → (base, prefix, k2)。
    
    例：
      QY-TH06055S 白+白   → base=06055S prefix=TH k2=False
      QY-TH06055S-K2 白   → base=06055S prefix=TH k2=True
      QY-WB06055S 白      → base=06055S prefix=WB k2=False
      QY-WB06055S-K2 白   → base=06055S prefix=WB k2=True
    """
    if not model:
        return None
    core = model.split()[0].strip()
    k2 = "-K2" in core.upper()
    core = re.sub(r"-K2$", "", core, flags=re.IGNORECASE)
    m = re.match(r"^QY-([A-Z]+)(\d+)([A-Za-z0-9]*)$", core)
    if not m:
        return None
    prefix = m.group(1)
    base = f"{m.group(2)}{m.group(3)}"
    return {"base": base, "prefix": prefix, "k2": k2, "full": model}


def extract_series_from_params(params_text: str) -> list:
    found = []
    if not params_text:
        return found
    for kw in SERIES_KEYWORDS:
        if kw in params_text:
            found.append(kw)
    return found


def extract_series_from_row(sname: str, row: tuple) -> dict:
    """从一行完整数据中提取系列线索。
    
    返回 {"sources": {...}, "candidates": set}
    """
    sources = {}
    candidates = set()
    # A列
    val_a = str(row[0] or "").strip() if len(row) > 0 else ""
    if val_a:
        sources["A列"] = val_a
    # G列
    val_g = str(row[6] or "").strip() if len(row) > 6 else ""
    if val_g:
        sources["G列"] = val_g
    # Sheet名（分类）
    if sname:
        sources["Sheet"] = sname
    # 参数中的系列关键词
    val_e = str(row[4] or "").strip() if len(row) > 4 else ""
    if val_e:
        for kw in SERIES_KEYWORDS:
            if kw in val_e:
                candidates.add(kw)
    # 名称字段（E列第一行 "1.名称：xxx"）
    name_m = re.search(r"名称[:：](.+)", val_e) if val_e else None
    if name_m:
        name = name_m.group(1).strip()
        for kw in SERIES_KEYWORDS:
            if kw in name:
                candidates.add(kw)
    return {"sources": sources, "candidates": candidates}


def extract_series_from_zh_params(zh_text: str) -> list:
    """从预埋盒参数中提取系列名（如 "预埋盒(魔方/柔光三代/明秀2.0）"）。"""
    found = []
    if not zh_text:
        return found
    # 括号内的系列名
    m = re.search(r"[（(]([^）)]*)[）)]", zh_text)
    if m:
        for kw in SERIES_KEYWORDS:
            if kw in m.group(1):
                found.append(kw)
    return found


def main():
    print(f"读取产品库: {DB_PATH}")
    wb = openpyxl.load_workbook(DB_PATH, data_only=True)

    # ── 第一步：扫描所有产品（读取完整行）──
    all_products = []
    for sname in wb.sheetnames:
        if "恒流" in sname:
            continue
        ws = wb[sname]
        for row_idx in range(3, (ws.max_row or 3) + 1):
            row_vals = tuple(
                ws.cell(row=row_idx, column=c).value
                for c in range(1, 10)
            )
            c4 = str(row_vals[3] or "").strip() if len(row_vals) > 3 else ""
            if not c4:
                continue
            all_products.append((sname, row_idx, row_vals))
    print(f"扫描到 {len(all_products)} 行产品")

    # ── 第二步：按基础型号归组 ──
    # base -> {"TH": model, "TH_K2": model, "WB": model, "WB_K2": model, "series": set, "holes": set}
    groups = OrderedDict()
    for sname, row_idx, row_vals in all_products:
        model = str(row_vals[3] or "").strip()
        params = str(row_vals[4] or "").strip()
        hole = str(row_vals[5] or "").strip()
        info = parse_model_info(model)
        if not info:
            continue
        base = info["base"]
        g = groups.setdefault(base, {
            "TH": "", "TH_K2": "", "WB": "", "WB_K2": "",
            "series": set(), "holes": set(), "series_source": "",
        })
        key = info["prefix"] + ("_K2" if info["k2"] else "")
        if key in g and not g[key]:
            g[key] = info["full"]
        # 开孔记录（辅助）
        clean_hole = re.sub(r"[^0-9x*]", "", hole) or hole
        g["holes"].add(clean_hole)
        # 系列候选：产品库各字段（记录来源字段）
        row_series = extract_series_from_row(sname, row_vals)
        for s in row_series["candidates"]:
            g["series"].add(s)
            if not g["series_source"]:
                # 记录哪个字段命中：优先 A/G/Sheet/名称
                if row_series["sources"].get("A列") and s in row_series["sources"].get("A列", ""):
                    g["series_source"] = "产品库字段(A列)"
                elif row_series["sources"].get("G列") and s in row_series["sources"].get("G列", ""):
                    g["series_source"] = "产品库字段(G列)"
                elif s in sname:
                    g["series_source"] = "Sheet名称"
                else:
                    g["series_source"] = "参数(E列)"

    print(f"构建到 {len(groups)} 个基础型号组")

    # ── 第三步：每组建一次系列名（产品库优先，兜底规则最后）──
    # 先收集预埋盒参数中的系列名（作为产品库的一部分）
    zh_series_map = {}
    for sname, row_idx, row_vals in all_products:
        model = str(row_vals[3] or "").strip()
        if re.match(r"^QY-ZH", model):
            zh_series_map[model] = str(row_vals[4] or "")

    for base, g in groups.items():
        # 优先级 1：产品库字段已识别的系列（A/G/Sheet/名称/参数）
        # 已在第二步收集到 g["series"]
        # 优先级 2：通过预埋盒配套关系补充
        if not g["series"]:
            g["series_source"] = "预埋盒配套关系"
            for key, full_model in list(g.items()):
                if not key.startswith("WB") or not isinstance(full_model, str) or not full_model:
                    continue
                short = full_model.replace("QY-", "").split()[0]
                for zh_model, zh_text in zh_series_map.items():
                    if short in zh_text:
                        for s in extract_series_from_zh_params(zh_text):
                            g["series"].add(s)
                        break
        # 优先级 3：兜底规则
        if not g["series"]:
            g["series_source"] = "Fallback规则"
            for kw, series in FALLBACK_SERIES_RULES:
                if kw in base:
                    g["series"].add(series)
                    break
        # 优先级 4：未知
        if not g["series"]:
            g["series"].add("未知")
            g["series_source"] = "未知"

    # ── 第四步：输出映射表 ──
    print("\n系列\t基础型号\t普通\t普通K2\t预埋\t预埋K2\t开孔")
    for base, g in groups.items():
        series = " / ".join(sorted(g["series"]))
        normal = g["TH"]
        normal_k2 = g["TH_K2"] or (normal.replace("-K2", "") + "-K2" if normal and "-K2" not in normal else "")
        pre = g["WB"]
        pre_k2 = g["WB_K2"] or (pre.replace("-K2", "") + "-K2" if pre and "-K2" not in pre else "")
        holes = " / ".join(sorted(g["holes"])) or "?"
        print(f"{series}\t{base}\t{normal}\t{normal_k2}\t{pre}\t{pre_k2}\t{holes}")

    # ── 系列来源统计 ──
    print("\n==== 1. 系列来源统计 ====")
    source_stats = {}
    for base, g in groups.items():
        src = g.get("series_source", "未知")
        source_stats[src] = source_stats.get(src, 0) + 1
    for src, cnt in sorted(source_stats.items(), key=lambda x: -x[1]):
        print(f"{src}: {cnt} 组")
    print("========================")

    # ── 2. 映射完整性检查 ──
    print("\n==== 2. 映射完整性检查 ====")
    complete_groups = 0
    incomplete_groups = 0
    for base, g in groups.items():
        series = " / ".join(sorted(g["series"]))
        normal = g["TH"]
        normal_k2 = g["TH_K2"] or (normal.replace("-K2", "") + "-K2" if normal and "-K2" not in normal else "")
        pre = g["WB"]
        pre_k2 = g["WB_K2"] or (pre.replace("-K2", "") + "-K2" if pre and "-K2" not in pre else "")
        checks = {
            "normal": normal,
            "normal_k2": normal_k2,
            "pre_embedded": pre,
            "pre_embedded_k2": pre_k2,
        }
        marks = []
        for k, v in checks.items():
            marks.append(("✓" if v else "✗") + " " + k)
        print(f"系列: {series}")
        print(f"基础型号: {base}")
        print("  " + "  ".join(marks))
        if all(checks.values()):
            complete_groups += 1
        else:
            incomplete_groups += 1
    print(f"\n完整产品组: {complete_groups}")
    print(f"缺失产品组: {incomplete_groups}")
    print("======================")

    # ── 3. Unknown 清单 ──
    print("\n==== 3. Unknown 清单 ====")
    unknown_count = 0
    for base, g in groups.items():
        if "未知" in g["series"] and len(g["series"]) == 1:
            unknown_count += 1
            # 分析原因
            has_wb = bool(g["WB"] or g["WB_K2"])
            has_th = bool(g["TH"] or g["TH_K2"])
            reason = []
            if not has_wb and not has_th:
                reason.append("产品库无 TH/WB 型号")
            if not g.get("series_source"):
                reason.append("来源字段为空")
            if not reason:
                reason.append("产品库不存在系列信息")
            print(f"Unknown: {base}")
            print(f"  原因: {', '.join(reason)}")
            print(f"  TH: {g['TH'] or '空'}  WB: {g['WB'] or '空'}")
    print(f"Unknown 总数: {unknown_count}")
    print("========================")

    # ── 4. Fallback 使用清单 ──
    print("\n==== 4. Fallback 使用清单 ====")
    fallback_count = 0
    for base, g in groups.items():
        if g.get("series_source") == "Fallback规则":
            fallback_count += 1
            print(f"{base}  Fallback: {' / '.join(sorted(g['series']))}")
    print(f"Fallback 总数: {fallback_count}")
    print("========================")

    # ── 第五步：按系列名汇总，更新 product_series.json ──
    if os.path.exists(SERIES_JSON):
        with open(SERIES_JSON, "r", encoding="utf-8-sig") as f:
            cfg = json.load(f)
    else:
        cfg = {"series": []}

    # 每个系列取第一个基础型号组的映射
    series_models = {}
    for base, g in groups.items():
        normal = g["TH"]
        normal_k2 = g["TH_K2"] or (normal.replace("-K2", "") + "-K2" if normal else "")
        pre = g["WB"]
        pre_k2 = g["WB_K2"] or (pre.replace("-K2", "") + "-K2" if pre else "")
        if not normal and not pre:
            continue
        for s in g["series"]:
            if s == "未知":
                continue
            if s not in series_models:
                series_models[s] = {
                    "normal": normal, "normal_k2": normal_k2,
                    "pre_embedded": pre, "pre_embedded_k2": pre_k2,
                }

    updated = 0
    for s in cfg.get("series", []):
        name = s.get("name", "")
        if name in series_models:
            s["models"] = series_models[name]
            print(f"\n[更新] {name}: {s['models']}")
            updated += 1

    with open(SERIES_JSON, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)
    print(f"\n已更新 {updated} 个系列，写入 {SERIES_JSON}")

    # ── 5. product_series.json 验证 ──
    print("\n==== 5. product_series.json 验证 ====")
    validation_errors = []
    with open(SERIES_JSON, "r", encoding="utf-8-sig") as f:
        saved_cfg = json.load(f)
    for s in saved_cfg.get("series", []):
        name = s.get("name", "")
        models = s.get("models", {})
        if not models:
            validation_errors.append(f"{name}: 无 models")
            continue
        for k in ("normal", "normal_k2", "pre_embedded", "pre_embedded_k2"):
            v = models.get(k, "")
            if not v:
                validation_errors.append(f"{name}: {k} 为空")
    # 重复/不存在型号检查
    all_models_in_db = set()
    for base, g in groups.items():
        for k in ("TH", "TH_K2", "WB", "WB_K2"):
            if g.get(k):
                all_models_in_db.add(g[k].split()[0])
    json_models = set()
    for s in saved_cfg.get("series", []):
        for k in ("normal", "normal_k2", "pre_embedded", "pre_embedded_k2"):
            v = (s.get("models", {}) or {}).get(k, "")
            if v:
                json_models.add(v.split()[0])
    not_in_db = json_models - all_models_in_db
    if not_in_db:
        validation_errors.append(f"不存在于产品库: {sorted(not_in_db)}")
    if validation_errors:
        print("Validation Failed")
        for e in validation_errors:
            print(f"  {e}")
    else:
        print("Validation Passed")
    print("===============================")

    wb.close()


if __name__ == "__main__":
    main()
