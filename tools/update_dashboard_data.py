from __future__ import annotations

import json
import math
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "streamlit_html_portal" / "static"
SALES_STATIC = STATIC_DIR / "2026-sales-dashboard.html"
YOY_STATIC = STATIC_DIR / "2026-vs-2025-yoy-dashboard.html"

F_DIR = Path("F:/llqdocument/大成文件/客户贡献分析")
SOURCE_2026_NAME = "PFS 26年毛利表1-6月 含电商 TOP20新.xlsx"
SOURCE_2025_NAME = "PFS 25年毛利表1-6月 含电商 TOP20 -品项实际 -新.xlsx"
SALES_SOURCE_HTML = F_DIR / "2026年1-6月数据分析仪表盘.html"
YOY_SOURCE_HTML = F_DIR / "26年与25年_1-6月数据对比分析.html"

BAD_CODES = {"CA2428001", "CC1131011"}
DELETE_MARKER = "删"


def find_source_file(name: str) -> Path:
    for root in (F_DIR, Path("E:/")):
        if not root.exists():
            continue
        for path in root.rglob(name):
            if path.is_file():
                return path
    raise FileNotFoundError(f"Cannot find source workbook: {name}")


def copy_sources_to_f_dir() -> tuple[Path, Path]:
    F_DIR.mkdir(parents=True, exist_ok=True)
    src_2026 = find_source_file(SOURCE_2026_NAME)
    src_2025 = find_source_file(SOURCE_2025_NAME)
    dst_2026 = F_DIR / SOURCE_2026_NAME
    dst_2025 = F_DIR / SOURCE_2025_NAME
    if src_2026.resolve() != dst_2026.resolve():
        shutil.copy2(src_2026, dst_2026)
    if src_2025.resolve() != dst_2025.resolve():
        shutil.copy2(src_2025, dst_2025)
    return dst_2026, dst_2025


def extract_app_data(text: str) -> tuple[int, int, dict[str, Any]]:
    match = re.search(r"(?:const|let|var)\s+APP_DATA\s*=\s*", text)
    if not match:
        raise ValueError("APP_DATA assignment not found")

    start = match.end()
    while start < len(text) and text[start].isspace():
        start += 1
    if start >= len(text) or text[start] not in "{[":
        raise ValueError("APP_DATA does not start with an object or array")

    stack: list[str] = []
    in_string = False
    quote = ""
    escaped = False
    for pos in range(start, len(text)):
        char = text[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                in_string = False
            continue
        if char in ('"', "'"):
            in_string = True
            quote = char
        elif char in "[{":
            stack.append("}" if char == "{" else "]")
        elif char in "]}":
            if not stack or char != stack[-1]:
                raise ValueError("Unbalanced APP_DATA JSON")
            stack.pop()
            if not stack:
                raw = text[start : pos + 1]
                return start, pos + 1, json.loads(raw)
    raise ValueError("APP_DATA JSON end not found")


def replace_app_data(path: Path, data: dict[str, Any]) -> None:
    text = path.read_text(encoding="utf-8", errors="replace")
    start, end, _ = extract_app_data(text)
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    path.write_text(text[:start] + payload + text[end:], encoding="utf-8")


def load_app_data(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    _, _, data = extract_app_data(text)
    return data


def clean_str(value: Any) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)) or pd.isna(value):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def clean_code(value: Any) -> str:
    text = clean_str(value)
    if text.endswith(".0"):
        return text[:-2]
    return text


def num(value: Any) -> float:
    if value is None or pd.isna(value):
        return 0.0
    parsed = pd.to_numeric(value, errors="coerce")
    if pd.isna(parsed):
        return 0.0
    return float(parsed)


def k(value: float, digits: int = 6) -> float:
    result = value / 1000.0
    if abs(result) < 0.0000005:
        return 0.0
    return round(result, digits)


def month_2026(value: Any) -> tuple[str, str]:
    raw = clean_code(value)
    if not raw:
        return "", ""
    if raw.startswith("26") and len(raw) >= 4:
        month = int(raw[-2:])
        return f"2026.{month:02d}", f"26{month:02d}"
    month = int(float(raw))
    return f"2026.{month:02d}", f"26{month:02d}"


def month_cn(value: Any, year: str) -> str:
    raw = clean_str(value)
    if not raw:
        return ""
    if raw.endswith("月"):
        return raw
    if raw.startswith("26") and len(raw) >= 4:
        return f"{int(raw[-2:])}月"
    return f"{int(float(raw))}月"


def most_common_lookup(records: list[dict[str, Any]], key: str, fields: tuple[str, ...]) -> dict[str, dict[str, str]]:
    buckets: dict[str, Counter[tuple[str, ...]]] = defaultdict(Counter)
    for record in records:
        key_value = clean_code(record.get(key))
        if not key_value:
            continue
        values = tuple(clean_str(record.get(field)) for field in fields)
        if any(values):
            buckets[key_value][values] += 1
    return {item_key: dict(zip(fields, counter.most_common(1)[0][0])) for item_key, counter in buckets.items()}


def build_lookup_context(sales_data: dict[str, Any], yoy_data: dict[str, Any]) -> dict[str, Any]:
    sales_records = sales_data.get("records", [])
    yoy_records = yoy_data.get("records", [])
    return {
        "sales_customer": most_common_lookup(sales_records, "cid", ("p", "ct", "ch", "nr", "mcid", "mcn")),
        "sales_customer_name": most_common_lookup(sales_records, "cn", ("p", "ct", "ch", "nr", "mcid", "mcn")),
        "sales_office": most_common_lookup(sales_records, "o", ("ch", "nr")),
        "yoy_customer": most_common_lookup(yoy_records, "mcid", ("p", "ct", "ch")),
        "yoy_customer_name": most_common_lookup(yoy_records, "mcn", ("p", "ct", "ch")),
        "yoy_office": most_common_lookup(yoy_records, "o", ("ch",)),
    }


def read_workbook(path: Path, sheet: str) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet, header=1, engine="openpyxl")


def has_delete_marker(*values: Any) -> bool:
    return any(DELETE_MARKER in clean_str(value) for value in values)


def filter_2026(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    code = df["物料号"].map(clean_code)
    office = df["列1"].map(clean_code) if "列1" in df.columns else df["销售办事处"].map(clean_code)
    delete_mask = df.apply(lambda row: has_delete_marker(row.get("物料描述"), row.get("品类"), row.get("品项")), axis=1)
    fake_mask = code.isin(BAD_CODES) | delete_mask
    office_3005_mask = office.str.startswith("3005", na=False)
    kept = df[~fake_mask & ~office_3005_mask].copy()
    return kept, {
        "raw_rows": int(len(df)),
        "kept_gross_income_k": k(kept["销售额"].map(num).sum()),
        "excluded_fake_product_rows": int(fake_mask.sum()),
        "excluded_fake_product_income_k": k(df.loc[fake_mask, "销售收入"].map(num).sum()),
        "excluded_fake_product_net_margin_k": k(df.loc[fake_mask, "扣除折让运费净边贡"].map(num).sum()),
        "excluded_fake_product_volume_ton": k(df.loc[fake_mask, "销量KG"].map(num).sum()),
        "excluded_3005_rows": int((~fake_mask & office_3005_mask).sum()),
        "excluded_3005_income_k": k(df.loc[~fake_mask & office_3005_mask, "销售收入"].map(num).sum()),
        "excluded_3005_net_margin_k": k(df.loc[~fake_mask & office_3005_mask, "扣除折让运费净边贡"].map(num).sum()),
        "excluded_3005_volume_ton": k(df.loc[~fake_mask & office_3005_mask, "销量KG"].map(num).sum()),
    }


def filter_2025(df: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    code = df["物料号"].map(clean_code)
    delete_mask = df.apply(lambda row: has_delete_marker(row.get("物料描述"), row.get("品类"), row.get("品项")), axis=1)
    fake_mask = code.isin(BAD_CODES) | delete_mask
    kept = df[~fake_mask].copy()
    return kept, {
        "raw_rows": int(len(df)),
        "excluded_fake_product_rows": int(fake_mask.sum()),
        "excluded_fake_product_income_k": k(df.loc[fake_mask, "销售收入"].map(num).sum()),
        "excluded_fake_product_net_margin_k": k(df.loc[fake_mask, "扣除折让运费的净边贡"].map(num).sum()),
        "excluded_fake_product_volume_ton": k(df.loc[fake_mask, "销量KG"].map(num).sum()),
    }


def enrich_sales(record: dict[str, Any], context: dict[str, Any]) -> dict[str, str]:
    cid = clean_code(record.get("客户编码"))
    cn = clean_str(record.get("客户描述"))
    office = clean_str(record.get("销售办事处"))
    info = context["sales_customer"].get(cid) or context["sales_customer_name"].get(cn) or {}
    office_info = context["sales_office"].get(office) or {}
    return {
        "p": info.get("p", "未识别"),
        "ct": info.get("ct", "未识别"),
        "ch": info.get("ch") or office_info.get("ch", "未识别"),
        "nr": info.get("nr") or office_info.get("nr", "未识别"),
        "mcid": info.get("mcid") or cid,
        "mcn": info.get("mcn") or cn,
    }


def enrich_yoy(customer_id: str, customer_name: str, office: str, context: dict[str, Any]) -> dict[str, str]:
    info = context["yoy_customer"].get(customer_id) or context["yoy_customer_name"].get(customer_name) or {}
    office_info = context["yoy_office"].get(office) or {}
    return {
        "p": info.get("p", "未识别"),
        "ct": info.get("ct", "未识别"),
        "ch": info.get("ch") or office_info.get("ch", "未识别"),
    }


def build_sales_records(df: pd.DataFrame, context: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in df.to_dict("records"):
        mo, mr = month_2026(row.get("月份"))
        enriched = enrich_sales(row, context)
        records.append({
            "mo": mo,
            "mr": mr,
            "o": clean_str(row.get("销售办事处")),
            "nr": enriched["nr"],
            "ch": enriched["ch"],
            "cid": clean_code(row.get("客户编码")),
            "cn": clean_str(row.get("客户描述")),
            "mcid": enriched["mcid"],
            "mcn": enriched["mcn"],
            "p": enriched["p"],
            "ct": enriched["ct"],
            "pc": clean_code(row.get("物料号")),
            "pn": clean_str(row.get("物料描述")),
            "cat": clean_str(row.get("品类")),
            "item": clean_str(row.get("品项")),
            "v": k(num(row.get("销量KG"))),
            "inc": k(num(row.get("销售收入"))),
            "dt": k(num(row.get("返利"))),
            "am": k(num(row.get("实际出厂边贡"))),
            "fr": k(num(row.get("运费合计"))),
            "ad": k(num(row.get("分摊折让"))),
            "nm": k(num(row.get("扣除折让运费净边贡"))),
        })
    return records


def build_yoy_rows_2025(df: pd.DataFrame, context: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in df.to_dict("records"):
        customer_id = clean_code(row.get("客户编码"))
        customer_name = clean_str(row.get("客户描述"))
        office = clean_str(row.get("销售办事处"))
        enriched = enrich_yoy(customer_id, customer_name, office, context)
        records.append({
            "y": "2025",
            "mo": month_cn(row.get("月份"), "2025"),
            "cat": clean_str(row.get("品类")),
            "item": clean_str(row.get("品项")),
            "ch": enriched["ch"],
            "p": enriched["p"],
            "ct": enriched["ct"],
            "mcid": customer_id,
            "mcn": customer_name,
            "pc": clean_code(row.get("物料号")),
            "pn": clean_str(row.get("物料描述")),
            "o": office,
            "src": 1,
            "v": k(num(row.get("销量KG"))),
            "inc": k(num(row.get("销售收入"))),
            "ad": k(num(row.get("分摊的折让"))),
            "nm": k(num(row.get("扣除折让运费的净边贡"))),
        })
    return records


def build_yoy_rows_2026(df: pd.DataFrame, context: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for row in df.to_dict("records"):
        customer_id = clean_code(row.get("客户编码"))
        customer_name = clean_str(row.get("客户描述"))
        office = clean_str(row.get("销售办事处"))
        enriched = enrich_yoy(customer_id, customer_name, office, context)
        records.append({
            "y": "2026",
            "mo": month_cn(row.get("月份"), "2026"),
            "cat": clean_str(row.get("品类")),
            "item": clean_str(row.get("品项")),
            "ch": enriched["ch"],
            "p": enriched["p"],
            "ct": enriched["ct"],
            "mcid": customer_id,
            "mcn": customer_name,
            "pc": clean_code(row.get("物料号")),
            "pn": clean_str(row.get("物料描述")),
            "o": office,
            "src": 1,
            "v": k(num(row.get("销量KG"))),
            "inc": k(num(row.get("销售收入"))),
            "ad": k(num(row.get("分摊折让"))),
            "nm": k(num(row.get("扣除折让运费净边贡"))),
        })
    return records


def aggregate_yoy(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dims = ("y", "mo", "cat", "item", "ch", "p", "ct", "mcid", "mcn", "pc", "pn", "o")
    grouped: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in records:
        key = tuple(record[dim] for dim in dims)
        if key not in grouped:
            grouped[key] = {dim: record[dim] for dim in dims}
            grouped[key].update({"src": 0, "v": 0.0, "inc": 0.0, "ad": 0.0, "nm": 0.0})
        target = grouped[key]
        target["src"] += int(record.get("src") or 1)
        target["v"] += float(record.get("v") or 0)
        target["inc"] += float(record.get("inc") or 0)
        target["ad"] += float(record.get("ad") or 0)
        target["nm"] += float(record.get("nm") or 0)
    result = list(grouped.values())
    for record in result:
        record["v"] = round(record["v"], 6)
        record["inc"] = round(record["inc"], 6)
        record["ad"] = round(record["ad"], 6)
        record["nm"] = round(record["nm"], 6)
    result.sort(key=lambda item: (item["y"], item["mo"], item["cat"], item["item"], item["ch"], item["p"], item["ct"], item["mcid"], item["pc"], item["o"]))
    return result


def totals(records: list[dict[str, Any]]) -> dict[str, float]:
    volume = sum(float(record.get("v") or 0) for record in records)
    income = sum(float(record.get("inc") or 0) for record in records)
    allocated_discount = sum(float(record.get("ad") or 0) for record in records)
    net_margin = sum(float(record.get("nm") or 0) for record in records)
    net_margin_base = income - allocated_discount
    return {
        "volume_ton": round(volume, 6),
        "income_k": round(income, 6),
        "allocated_discount_k": round(allocated_discount, 6),
        "net_margin_base_k": round(net_margin_base, 6),
        "net_margin_k": round(net_margin, 6),
        "net_margin_rate": net_margin / net_margin_base if net_margin_base else 0.0,
    }


def update_quality_sales(data: dict[str, Any], records: list[dict[str, Any]], source_2026: Path, stats_2026: dict[str, Any]) -> None:
    quality = data.setdefault("quality", {})
    quality["period"] = "2026.01-2026.06"
    quality["source"] = str(source_2026)
    quality["income_metric_source"] = "销售收入（未税收入）"
    quality["gross_income_metric_source"] = "销售额（含税销额，仅作参考）"
    quality["net_margin_rate_formula"] = "扣除折让运费后的净边贡 / (销售收入 - 分摊后折让)"
    quality["rows"] = len(records)
    quality["month_order"] = ["2026.01", "2026.02", "2026.03", "2026.04", "2026.05", "2026.06"]
    quality["sku_cnt"] = len({record["pc"] for record in records if record.get("pc")})
    quality["customer_cnt"] = len({record["cid"] for record in records if record.get("cid")})
    quality["merged_customer_cnt"] = len({record["mcid"] for record in records if record.get("mcid")})
    quality["category_cnt"] = len({record["cat"] for record in records if record.get("cat")})
    quality["item_cnt"] = len({record["item"] for record in records if record.get("item")})
    quality["channel_cnt"] = len({record["ch"] for record in records if record.get("ch")})
    total_volume = sum(float(record.get("v") or 0) for record in records)
    total_income = sum(float(record.get("inc") or 0) for record in records)
    total_allocated_discount = sum(float(record.get("ad") or 0) for record in records)
    total_net_margin = sum(float(record.get("nm") or 0) for record in records)
    total_net_margin_base = total_income - total_allocated_discount
    quality["total_volume_ton"] = round(total_volume, 6)
    quality["total_gross_income_k"] = stats_2026["kept_gross_income_k"]
    quality["total_income_k"] = round(total_income, 6)
    quality["total_allocated_discount_k"] = round(total_allocated_discount, 6)
    quality["total_net_margin_base_k"] = round(total_net_margin_base, 6)
    quality["total_net_margin_k"] = round(total_net_margin, 6)
    quality["net_margin_rate"] = total_net_margin / total_net_margin_base if total_net_margin_base else 0.0
    quality["excluded_fake_product_rows"] = stats_2026["excluded_fake_product_rows"]
    quality["excluded_fake_product_income_k"] = stats_2026["excluded_fake_product_income_k"]
    quality["excluded_fake_product_volume_ton"] = stats_2026["excluded_fake_product_volume_ton"]
    quality["excluded_fake_product_net_margin_k"] = stats_2026["excluded_fake_product_net_margin_k"]
    quality["excluded_3005_rows"] = stats_2026["excluded_3005_rows"]
    quality["excluded_3005_income_k"] = stats_2026["excluded_3005_income_k"]
    quality["excluded_3005_volume_ton"] = stats_2026["excluded_3005_volume_ton"]
    quality["excluded_3005_net_margin_k"] = stats_2026["excluded_3005_net_margin_k"]
    quality["missing_customer_cnt"] = len({record["cid"] for record in records if record.get("p") == "未识别"})


def update_quality_yoy(data: dict[str, Any], records: list[dict[str, Any]], source_2025: Path, source_2026: Path, stats_2025: dict[str, Any], stats_2026: dict[str, Any]) -> None:
    quality = data.setdefault("quality", {})
    quality["source_2025"] = str(source_2025)
    quality["source_2026"] = str(source_2026)
    quality["income_metric_source_2026"] = "销售收入（未税收入）"
    quality["income_metric_source_2025"] = "销售收入（未税收入）"
    quality["gross_income_metric_source_2026"] = "销售额（含税销额，仅作参考）"
    quality["gross_income_metric_source_2025"] = "销售额（含税销额，仅作参考）"
    quality["net_margin_rate_formula"] = "扣除折让运费后的净边贡 / (销售收入 - 分摊后折让)"
    column_map = quality.setdefault("metric_column_map", {})
    column_map.setdefault("2026", {})["income"] = "销售收入 / 1000（未税收入）"
    column_map.setdefault("2026", {})["gross_income"] = "销售额 / 1000（含税销额，仅作参考）"
    column_map.setdefault("2025", {})["income"] = "销售收入 / 1000（未税收入）"
    column_map.setdefault("2025", {})["gross_income"] = "销售额 / 1000（含税销额，仅作参考）"
    quality["aggregated_rows"] = len(records)
    quality["category_cnt"] = len({record["cat"] for record in records if record.get("cat")})
    quality["totals"] = {
        "2025": totals([record for record in records if record.get("y") == "2025"]),
        "2026": totals([record for record in records if record.get("y") == "2026"]),
    }
    quality["raw_rows_2025"] = stats_2025["raw_rows"]
    quality["excluded_fake_product_rows_2025"] = stats_2025["excluded_fake_product_rows"]
    quality["excluded_fake_product_income_k_2025"] = stats_2025["excluded_fake_product_income_k"]
    quality["excluded_fake_product_net_margin_k_2025"] = stats_2025["excluded_fake_product_net_margin_k"]
    quality["excluded_fake_product_volume_ton_2025"] = stats_2025["excluded_fake_product_volume_ton"]
    quality["raw_rows_2026"] = stats_2026["raw_rows"]
    quality["excluded_fake_product_rows_2026"] = stats_2026["excluded_fake_product_rows"]
    quality["excluded_fake_product_income_k_2026"] = stats_2026["excluded_fake_product_income_k"]
    quality["excluded_fake_product_net_margin_k_2026"] = stats_2026["excluded_fake_product_net_margin_k"]
    quality["excluded_fake_product_volume_ton_2026"] = stats_2026["excluded_fake_product_volume_ton"]
    quality["excluded_3005_rows"] = stats_2026["excluded_3005_rows"]
    quality["excluded_3005_income_k"] = stats_2026["excluded_3005_income_k"]
    quality["excluded_3005_net_margin_k"] = stats_2026["excluded_3005_net_margin_k"]
    quality["excluded_3005_volume_ton"] = stats_2026["excluded_3005_volume_ton"]


def main() -> None:
    source_2026, source_2025 = copy_sources_to_f_dir()
    sales_data = load_app_data(SALES_STATIC)
    yoy_data = load_app_data(YOY_STATIC)
    context = build_lookup_context(sales_data, yoy_data)

    df_2026 = read_workbook(source_2026, "26")
    df_2025 = read_workbook(source_2025, "25")
    clean_2026, stats_2026 = filter_2026(df_2026)
    clean_2025, stats_2025 = filter_2025(df_2025)

    sales_records = build_sales_records(clean_2026, context)
    yoy_raw = build_yoy_rows_2025(clean_2025, context) + build_yoy_rows_2026(clean_2026, context)
    yoy_records = aggregate_yoy(yoy_raw)

    sales_data["records"] = sales_records
    update_quality_sales(sales_data, sales_records, source_2026, stats_2026)
    yoy_data["records"] = yoy_records
    update_quality_yoy(yoy_data, yoy_records, source_2025, source_2026, stats_2025, stats_2026)

    for path, data in ((SALES_STATIC, sales_data), (YOY_STATIC, yoy_data)):
        replace_app_data(path, data)

    shutil.copy2(SALES_STATIC, SALES_SOURCE_HTML)
    shutil.copy2(YOY_STATIC, YOY_SOURCE_HTML)

    print(json.dumps({
        "source_2026": str(source_2026),
        "source_2025": str(source_2025),
        "sales_records": len(sales_records),
        "yoy_records": len(yoy_records),
        "sales_totals": totals(sales_records),
        "yoy_totals": yoy_data["quality"]["totals"],
        "stats_2026": stats_2026,
        "stats_2025": stats_2025,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
