import gzip
import json
import re

import pandas as pd

from tools.product_classification import is_excluded_pork_pie, product_dimensions, repair_product_rows
from tools.update_dashboard_data import SALES_STATIC, YOY_STATIC, fake_product_mask


def test_product_exclusion_keeps_other_products_and_office_adjustments():
    records = [
        ("CA2428001", "其他描述", "调理品", "其他"),
        ("OTHER", "香菇 豬肉派3000g×4", "调理品", "其他"),
        ("OTHER", "正常描述", "调理品", "香菇猪肉派"),
        ("OTHER", "香菇猪肉馅", "调理品", "其他"),
        (None, None, None, None),
    ]
    data = pd.DataFrame(records, columns=["物料号", "物料描述", "品类", "品项"])
    assert fake_product_mask(data).tolist() == [True, True, True, False, False]


def test_confirmed_product_categories_and_preserved_metrics():
    rows = [{'pc': 'CP3829005', 'pn': '奶酪丁', 'cat': '#N/A', 'item': '', 'v': 2, 'inc': 132}]
    repair_product_rows(rows)
    assert rows == [{'pc': 'CP3829005', 'pn': '奶酪丁', 'cat': '芝士类', 'item': '奶酪丁', 'v': 2, 'inc': 132}]
    assert product_dimensions('UNKNOWN', '新品', '#N/A', '#REF!') == ('未映射', '新品')
    assert product_dimensions('CP3829005', '名称', '芝士类', '正式品项') == ('芝士类', '正式品项')


def test_published_payloads_contain_no_blank_or_excel_error_dimensions():
    expected = {'CP3829005': ('芝士类', '高熔点奶酪', 2.0, 132.0),
                'CC1140005': ('盐酥鸡类', '胸盐', .72, 9.0),
                'CC7422005': ('裹粉原肉类', '裹粉猪排', .86, 22.36),
                'CK1122118': ('香肠类', '原味德肠', .984, 25.584)}
    for path in [SALES_STATIC, YOY_STATIC]:
        html = gzip.decompress(path.read_bytes()).decode()
        start = re.search(r'const APP_DATA\s*=\s*', html).end()
        data = json.JSONDecoder().raw_decode(html[start:])[0]
        for row in data['records']:
            assert row['cat'] and not row['cat'].startswith('#')
            assert row['item'] and not row['item'].startswith('#')
            assert not is_excluded_pork_pie(row.get('pc'), row.get('pn'), row['cat'], row['item'])
        for material, (category, item, volume, sales) in expected.items():
            rows = [
                row for row in data['records']
                if row['pc'] == material
                and (str(row.get('y')) == '2026' or row['mo'].startswith('2026.'))
            ]
            assert rows and all(row['cat'] == category and row['item'] == item for row in rows)
            assert abs(sum(row['v'] for row in rows) - volume) < 1e-8
            assert abs(sum(row['inc'] for row in rows) - sales) < 1e-8
