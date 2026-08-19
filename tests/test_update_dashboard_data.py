import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.update_dashboard_data import YOY_CHANNEL_ORDER, YOY_MONTH_ORDER, month_cn


ROOT = Path(__file__).resolve().parents[1]


def test_month_cn_normalizes_short_year_month_codes() -> None:
    assert month_cn("2501月", "2025") == "1月"
    assert month_cn("2507", "2025") == "7月"
    assert month_cn("2606月", "2026") == "6月"
    assert month_cn("2607", "2026") == "7月"


def test_month_cn_keeps_plain_month_values() -> None:
    assert month_cn("7月", "2025") == "7月"
    assert month_cn(7, "2026") == "7月"


def test_dashboard_filter_orders_include_latest_month_and_eight_channels() -> None:
    assert YOY_MONTH_ORDER == [f"{month}月" for month in range(1, 8)]
    assert YOY_CHANNEL_ORDER == ["烘焙", "休闲", "团膳", "宴席", "零售", "KA", "鲜食工厂", "其他"]


def test_dashboard_display_precision_contract() -> None:
    sales_html = (ROOT / "streamlit_html_portal/static/2026-sales-dashboard.html").read_text(encoding="utf-8")
    yoy_html = (ROOT / "streamlit_html_portal/static/2026-vs-2025-yoy-dashboard.html").read_text(encoding="utf-8")

    for metric in ["net_margin_k", "income_k", "actual_margin_k", "volume_ton", "discount_total_k", "freight_k"]:
        assert f"{metric}:{{" in sales_html
        metric_definition = sales_html.split(f"{metric}:{{", 1)[1].split("}", 1)[0]
        assert "decimals:0" in metric_definition

    assert "function fmt(n) { return Math.round(+n || 0).toLocaleString('zh-CN'); }" in yoy_html
    assert "function pct(n) { return Number.isFinite(n) ? (n*100).toFixed(1)+'%' : '-'; }" in yoy_html
