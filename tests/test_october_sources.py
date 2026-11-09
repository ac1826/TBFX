from tools.update_dashboard_data import (
    CUSTOMER_LIST_NAME, SOURCE_2025_NAME, SOURCE_2026_NAME, YOY_MONTH_ORDER,
    SALES_STATIC, YOY_STATIC, RESEARCHED_GEO, load_app_data, sync_available_periods,
)


def test_current_adjustments_match_revised_workbook():
    rows = load_app_data(SALES_STATIC)["netContributionAdjustments"]
    current = [row for row in rows if row["mr"].startswith("2026.")]
    prior = [row for row in rows if row["mr"].startswith("2025.")]
    assert len(prior) == 39
    assert len(current) == 26
    assert {month: sum(row["mr"] == month for row in current) for month in {row["mr"] for row in current}} == {
        "2026.08": 19, "2026.09": 7,
    }
    assert round(sum(row["nm"] for row in current), 6) == -123.55915
    assert round(sum(row["ad"] for row in current), 6) == 123.55915


def test_october_sources_and_months():
    assert '1-10月' in SOURCE_2025_NAME and '1-10月' in SOURCE_2026_NAME
    assert CUSTOMER_LIST_NAME == '客户清单_11.xlsx'
    assert YOY_MONTH_ORDER[-1] == '10月'
    for path in [SALES_STATIC, YOY_STATIC]:
        data = load_app_data(path)
        assert any(row.get('mo') in {'10月', '2026.10'} for row in data['records'])
    data = load_app_data(SALES_STATIC)
    assert {'2025.10', '2026.10'}.issubset(data['monthOrder'])
    assert data['monthOrder'] == sorted({row['mo'] for row in data['records']})


def test_available_periods_follow_detail_across_future_years():
    data = {'monthOrder': ['2025.09'], 'records': [
        {'mo': '2026.10'}, {'mo': '2025.10'}, {'mo': '2027.01'},
        {'mo': '2026.10'}, {'mo': ''},
    ]}
    sync_available_periods(data)
    assert data['monthOrder'] == ['2025.10', '2026.10', '2027.01']


def test_browser_month_options_ignore_stale_metadata():
    import gzip
    import re
    import subprocess
    html = gzip.decompress(SALES_STATIC.read_bytes()).decode('utf-8')
    declaration = re.search(r'const MONTH_ORDER = [^;]+;', html).group()
    script = (
        "const APP_DATA={monthOrder:['2025.09']};"
        "const RAW=[{mo:'2025.10'},{mo:'2026.10'},{mo:'2027.01'}];"
        + declaration
        + "if(JSON.stringify(MONTH_ORDER)!==JSON.stringify(['2025.10','2026.10','2027.01']))throw Error(JSON.stringify(MONTH_ORDER));"
    )
    subprocess.check_call(['node', '-e', script])


def test_user_confirmed_provinces_are_in_the_sales_snapshot():
    data = load_app_data(SALES_STATIC)
    assert RESEARCHED_GEO['299156']['p'] == '台湾省'
    expected = {'261172': ('广东省', '广州'), '274829': ('陕西省', '安康')}
    for customer, (province, city) in expected.items():
        rows = [row for row in data['records'] if row.get('cid') == customer]
        assert rows, customer
        assert all(row['p'] == province for row in rows)
        if city:
            assert all(row['ct'] == city for row in rows)
