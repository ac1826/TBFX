from tools.update_dashboard_data import (
    CUSTOMER_LIST_NAME, SOURCE_2025_NAME, SOURCE_2026_NAME, YOY_MONTH_ORDER,
    SALES_STATIC, YOY_STATIC, load_app_data,
)


def test_october_sources_and_months():
    assert '1-10月' in SOURCE_2025_NAME and '1-10月' in SOURCE_2026_NAME
    assert CUSTOMER_LIST_NAME == '客户清单_11.xlsx'
    assert YOY_MONTH_ORDER[-1] == '10月'
    for path in [SALES_STATIC, YOY_STATIC]:
        data = load_app_data(path)
        assert any(row.get('mo') in {'10月', '2026.10'} for row in data['records'])
    data = load_app_data(SALES_STATIC)
    assert {'2025.10', '2026.10'}.issubset(data['monthOrder'])
