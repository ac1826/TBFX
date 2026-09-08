import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from tools.update_dashboard_data import (
    YOY_CHANNEL_ORDER,
    YOY_MONTH_ORDER,
    city_from_sales_region,
    enrich_sales,
    first_present,
    load_app_data,
    month_cn,
    split_office_adjustments_2026,
    totals_with_adjustments,
)


ROOT = Path(__file__).resolve().parents[1]


def test_month_cn_normalizes_short_year_month_codes() -> None:
    assert month_cn("2501月", "2025") == "1月"
    assert month_cn("2507", "2025") == "7月"
    assert month_cn("2606月", "2026") == "6月"
    assert month_cn("2607", "2026") == "7月"
    assert month_cn("2608", "2026") == "8月"


def test_month_cn_keeps_plain_month_values() -> None:
    assert month_cn("7月", "2025") == "7月"
    assert month_cn(7, "2026") == "7月"


def test_dashboard_filter_orders_include_latest_month_and_eight_channels() -> None:
    assert YOY_MONTH_ORDER == [f"{month}月" for month in range(1, 9)]
    assert YOY_CHANNEL_ORDER == ["烘焙", "休闲", "团膳", "宴席", "零售", "KA", "鲜食工厂", "其他"]


def test_sales_region_explicitly_supplies_city() -> None:
    assert city_from_sales_region("江苏南通") == "南通"
    assert city_from_sales_region("河南省郑州市中牟县") == "郑州"
    assert city_from_sales_region("北京(省级)") == "北京"
    assert city_from_sales_region("南方地区") == ""


def test_name_consensus_fills_dimensions_without_merging_customer_identity() -> None:
    context = {
        "canonical_geo": {},
        "customer_cities": {},
        "org_customers": {},
        "reference_maps": {},
        "canonical_region": {"7350": "RKA"},
        "merged_customers": {},
        "canonical_channel": {},
        "customer_names": {},
        "listed_names": {},
        "name_dimension_index": {"苏州圆融享德来餐饮管": []},
        "resolve_name_dimensions": lambda _name, _index: {
            "status": "mapped",
            "channel": "KA",
            "province": "江苏省",
            "city": "苏州",
        },
    }

    enriched = enrich_sales(
        {"客户编码": "274770", "客户描述": "苏州圆融享德来餐饮管", "销售办事处": "7350 RKA"},
        context,
    )

    assert enriched["ch"] == "KA"
    assert enriched["p"] == "江苏省"
    assert enriched["ct"] == "苏州"
    assert enriched["mcid"] == "274770"
    assert enriched["mcn"] == "苏州圆融享德来餐饮管"
    assert enriched["name_match_status"] == "mapped"


def test_generated_enjoydelai_name_consensus_mapping_keeps_customer_ids() -> None:
    expected = {
        "274770", "274771", "274775", "274781", "274782",
        "274783", "274785", "274789", "274791",
    }
    unresolved = {"274777", "274778", "274779", "274787", "274790"}
    records = load_app_data(ROOT / "streamlit_html_portal/static/2026-sales-dashboard.html")["records"]
    mapped_rows = [row for row in records if row.get("cid") in expected]
    unresolved_rows = [row for row in records if row.get("cid") in unresolved]

    assert {row["cid"] for row in mapped_rows} == expected
    assert all((row["ch"], row["p"], row["ct"]) == ("KA", "江苏省", "苏州") for row in mapped_rows)
    assert all(row["mcid"] == row["cid"] for row in mapped_rows)
    assert {row["cid"] for row in unresolved_rows} == unresolved
    assert all(row["ch"] == "未映射" or row["p"] == "未识别省份" or row["ct"] == "未映射" for row in unresolved_rows)


def test_dashboard_display_precision_contract() -> None:
    sales_html = (ROOT / "streamlit_html_portal/static/2026-sales-dashboard.html").read_text(encoding="utf-8")
    yoy_html = (ROOT / "streamlit_html_portal/static/2026-vs-2025-yoy-dashboard.html").read_text(encoding="utf-8")

    for metric in ["net_margin_k", "income_k", "actual_margin_k", "volume_ton", "discount_total_k", "freight_k"]:
        assert f"{metric}:{{" in sales_html
        metric_definition = sales_html.split(f"{metric}:{{", 1)[1].split("}", 1)[0]
        assert "decimals:0" in metric_definition

    assert "function fmt(n) { return Math.round(+n || 0).toLocaleString('zh-CN'); }" in yoy_html
    assert "function pct(n) { return Number.isFinite(n) ? (n*100).toFixed(1)+'%' : '-'; }" in yoy_html


def test_2026_allocated_discount_accepts_old_and_new_column_names() -> None:
    assert first_present({"分摊折让": 12.5}, "分摊折让", "分摊后折让") == 12.5
    assert first_present({"分摊后折让": 18.75}, "分摊折让", "分摊后折让") == 18.75


def test_office_adjustments_are_split_from_rankable_detail() -> None:
    frame = pd.DataFrame([
        {
            "销售办事处": "7210 沈阳餐饮", "月份": 2601,
            "客户编码": None, "客户描述": None, "物料号": None, "物料描述": None,
            "品类": None, "品项": None, "销量KG": 0, "销售额": 0, "销售收入": 0,
            "折让合计": 0, "实际出厂边贡": 0, "运费合计": 0,
            "扣除折让运费净边贡": 3717.79, "分摊后折让": -3717.79,
        },
        {
            "销售办事处": "7210 沈阳餐饮", "月份": 2601,
            "客户编码": "100001", "客户描述": "客户", "物料号": "M1", "物料描述": "产品",
            "品类": "烘焙类", "品项": "面包", "销量KG": 1000, "销售额": 2000, "销售收入": 1800,
            "折让合计": 0, "实际出厂边贡": 500, "运费合计": 50,
            "扣除折让运费净边贡": 400, "分摊后折让": 50,
        },
    ])
    detail, adjustments = split_office_adjustments_2026(frame)
    assert len(detail) == 1
    assert len(adjustments) == 1
    assert adjustments.iloc[0]["扣除折让运费净边贡"] == 3717.79


def test_total_net_margin_adds_adjustment_without_changing_rate() -> None:
    detail = [{"v": 1, "inc": 100, "ni": 90, "ad": 10, "nm": 20}]
    combined = totals_with_adjustments(detail, [{"nm": 5, "ad": -5}])
    assert combined["net_margin_k"] == 25
    assert combined["net_margin_rate"] == 0.25
