import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.update_dashboard_data import YOY_CHANNEL_ORDER, YOY_MONTH_ORDER, month_cn


def test_month_cn_normalizes_short_year_month_codes() -> None:
    assert month_cn("2501月", "2025") == "1月"
    assert month_cn("2507", "2025") == "7月"
    assert month_cn("2606月", "2026") == "6月"
    assert month_cn("2607", "2026") == "7月"


def test_month_cn_keeps_plain_month_values() -> None:
    assert month_cn("7月", "2025") == "7月"
    assert month_cn(7, "2026") == "7月"


def test_yoy_filter_orders_include_latest_month_and_ecommerce() -> None:
    assert YOY_MONTH_ORDER == [f"{month}月" for month in range(1, 8)]
    assert "电商" in YOY_CHANNEL_ORDER
