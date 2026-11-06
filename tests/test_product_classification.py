import gzip
import json
import re

from tools.product_classification import product_dimensions, repair_product_rows
from tools.update_dashboard_data import SALES_STATIC, YOY_STATIC


def test_confirmed_product_categories_and_preserved_metrics():
    rows = [{'pc': 'CP3829005', 'pn': '奶酪丁', 'cat': '#N/A', 'item': '', 'v': 2, 'inc': 132}]
    repair_product_rows(rows)
    assert rows == [{'pc': 'CP3829005', 'pn': '奶酪丁', 'cat': '芝士类', 'item': '奶酪丁', 'v': 2, 'inc': 132}]
    assert product_dimensions('UNKNOWN', '新品', '#N/A', '#REF!') == ('未映射', '新品')
    assert product_dimensions('CP3829005', '名称', '芝士类', '正式品项') == ('芝士类', '正式品项')


def test_published_payloads_contain_no_blank_or_excel_error_dimensions():
    expected = {'CP3829005': '芝士类', 'CC1140005': '盐酥鸡类',
                'CC7422005': '裹粉原肉类', 'CK1122118': '香肠类'}
    for path in [SALES_STATIC, YOY_STATIC]:
        html = gzip.decompress(path.read_bytes()).decode()
        start = re.search(r'const APP_DATA\s*=\s*', html).end()
        data = json.JSONDecoder().raw_decode(html[start:])[0]
        for row in data['records']:
            assert row['cat'] and not row['cat'].startswith('#')
            assert row['item'] and not row['item'].startswith('#')
        for material, category in expected.items():
            rows = [row for row in data['records'] if row['pc'] == material]
            assert rows and all(row['cat'] == category and row['item'] == row['pn'] for row in rows)
