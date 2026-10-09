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


def test_rka_perimeter_is_comparable_without_moving_other_7550_customers() -> None:
    sys.path.insert(0, str(ROOT.parent / "pfs-profitability-dashboard"))
    from src.pipeline import comparable_region_2026
    context = {key: {} for key in (
        "canonical_geo", "customer_cities", "org_customers", "reference_maps",
        "merged_customers", "canonical_channel", "customer_names", "listed_names", "name_dimension_index",
    )}
    context.update(canonical_region={"7550": "华东区", "7559": "RKA"},
                   comparable_region_2026=comparable_region_2026, tastien_customers={"tst"},
                   resolve_name_dimensions=lambda *_: {"status": "no_candidate"})
    row = {"客户编码": "tst", "客户描述": "塔斯汀", "销售办事处": "7550 福建餐饮"}
    assert enrich_sales(row, context, 2025)["nr"] == "RKA"
    assert enrich_sales(row, context, 2025)["mcid"] == "tst"
    row["客户编码"] = "other"
    assert enrich_sales(row, context, 2025)["nr"] == "华东区"
    row["销售办事处"] = "7559 KA TST"
    assert enrich_sales(row, context, 2026)["nr"] == "RKA"


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
    assert YOY_MONTH_ORDER == [f"{month}月" for month in range(1, 10)]
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


def test_rka_customer_override_is_year_scoped_and_keeps_identity() -> None:
    context = {key: {} for key in (
        "canonical_geo", "customer_cities", "org_customers", "reference_maps",
        "canonical_region", "merged_customers", "canonical_channel", "customer_names",
        "listed_names", "name_dimension_index",
    )}
    context["user_rka_2026"] = {"274778"}
    context["resolve_name_dimensions"] = lambda *_: {"status": "no_candidate"}
    row = {"客户编码": "274778", "客户描述": "苏州市健善享德来餐饮", "销售办事处": "7350 RKA"}
    current = enrich_sales(row, context, 2026)
    previous = enrich_sales(row, context, 2025)
    assert (current["ch"], current["p"], current["ct"]) == ("KA", "江苏省", "苏州")
    assert current["mcid"] == "274778"
    assert previous["ch"] == "未映射"
    assert previous["p"] == "未识别省份"
    assert previous["ct"] == "未映射"
    row["销售办事处"] = "3005 电商"
    assert enrich_sales(row, context, 2026)["ch"] == "电商"


def test_confirmed_geography_overrides_old_location_without_changing_channel_or_identity() -> None:
    context = {key: {} for key in (
        "canonical_geo", "customer_cities", "org_customers", "reference_maps",
        "canonical_region", "merged_customers", "canonical_channel", "customer_names",
        "listed_names", "name_dimension_index",
    )}
    context["canonical_geo"] = {"274749": {"p": "江苏省", "ct": "苏州"}}
    context["canonical_channel"] = {"274749": "KA"}
    context["user_confirmed_geo_2026"] = {"274749": {"province": "浙江省", "city": "金华"}}
    context["resolve_name_dimensions"] = lambda *_: {"status": "no_candidate"}
    row = {"客户编码": "274749", "客户描述": "利她（义乌）餐饮管理有限公司", "销售办事处": "7350 RKA"}
    current = enrich_sales(row, context, 2026)
    previous = enrich_sales(row, context, 2025)
    assert (current["p"], current["ct"], current["ch"], current["mcid"]) == ("浙江省", "金华", "KA", "274749")
    assert (previous["p"], previous["ct"]) == ("江苏省", "苏州")


def test_generated_enjoydelai_name_consensus_mapping_keeps_customer_ids() -> None:
    expected = {
        "274770", "274771", "274775", "274781", "274782",
        "274783", "274785", "274789", "274791",
    }
    expected.update({"274772", "274773", "274774", "274776", "274777", "274778",
                     "274779", "274780", "274784", "274786", "274787"})
    records = load_app_data(ROOT / "streamlit_html_portal/static/2026-sales-dashboard.html")["records"]
    mapped_rows = [row for row in records if row.get("cid") in expected]

    assert {row["cid"] for row in mapped_rows} == expected
    assert all((row["ch"], row["p"], row["ct"]) == ("KA", "江苏省", "苏州") for row in mapped_rows)
    assert all(row["mcid"] == row["cid"] for row in mapped_rows)
    for customer, province, city in [
        ("274788", "浙江省", "宁波"), ("274790", "江苏省", "南京"),
        ("274723", "上海市", "上海"), ("274745", "辽宁省", "沈阳"),
        ("274747", "江苏省", "常州"), ("274751", "江苏省", "无锡"),
    ]:
        selected = [row for row in records if row.get("cid") == customer]
        assert selected
        assert all((row["ch"], row["p"], row["ct"], row["mcid"]) == ("KA", province, city, customer) for row in selected)


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
    prior = frame.rename(columns={
        "扣除折让运费净边贡": "扣除折让运费的净边贡",
        "分摊后折让": "分摊的折让",
    }).copy()
    prior["月份"] = 2508
    prior.loc[0, "扣除折让运费的净边贡"] = -9530
    prior.loc[0, "分摊的折让"] = 9530
    detail25, adjustments25 = split_office_adjustments_2026(prior, 2025)
    assert len(detail25) == len(adjustments25) == 1
    assert adjustments25.iloc[0]["扣除折让运费的净边贡"] == -9530


def test_yoy_adjustments_use_year_month_and_filter_scope() -> None:
    import re
    import subprocess
    html = (ROOT / "streamlit_html_portal/static/2026-vs-2025-yoy-dashboard.html").read_text(encoding="utf-8")
    names = ["adjustmentsAllowedInTotals", "adjustmentNetMargin", "summary", "totalSummary"]
    functions = "\n".join(re.search(r"    function " + name + r"\([^\n]*\) \{.*?\n    \}", html, re.S).group(0) for name in names)
    script = """
const assert = require('node:assert/strict');
let filters={}, selectedProvince=null, selectedCity=null;
const selectedValues=k=>filters[k]||null;
const document={getElementById:()=>({value:''})};
const MONTH_ORDER=['7月','8月']; const yoy=(a,b)=>a/b-1;
const NET_CONTRIBUTION_ADJUSTMENTS=[{y:'2025',mo:'8月',nm:-9.052},{y:'2026',mo:'8月',nm:20}];
""" + functions + """
const rows=[{y:'2025',nm:100,inc:1000},{y:'2026',nm:200,inc:2000}];
assert.ok(Math.abs(totalSummary(rows,'nm',['8月']).v25-90.948)<1e-9);
assert.equal(totalSummary(rows,'nm',['8月']).v26,220);
assert.equal(totalSummary(rows,'nm',['7月']).v25,100);
assert.equal(totalSummary(rows,'inc',['8月']).v25,1000);
assert.equal(summary(rows,'nm').v25,100);
for(const key of ['categoryFilter','channelFilter']) { filters={[key]:['chosen']}; assert.equal(totalSummary(rows,'nm').v25,100); }
filters={}; selectedProvince='江苏省'; assert.equal(totalSummary(rows,'nm').v25,100);
"""
    result = subprocess.run(["node", "-e", script], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_total_net_margin_adds_adjustment_without_changing_rate() -> None:
    detail = [{"v": 1, "inc": 100, "ni": 90, "ad": 10, "nm": 20}]
    combined = totals_with_adjustments(detail, [{"nm": 5, "ad": -5}])
    assert combined["net_margin_k"] == 25
    assert combined["net_margin_rate"] == 0.25
