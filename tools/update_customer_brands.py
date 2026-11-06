"""Validate an explicit KA customer/brand register before replacing its snapshot."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import openpyxl


def identifier(value: object) -> str:
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def brand_mapping(rows: list[tuple]) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for row in rows:
        customer, brand = identifier(row[3]), identifier(row[2])
        if not customer and not brand:
            continue
        if not customer or not brand or customer.startswith('#') or brand.startswith('#'):
            raise ValueError(f'Incomplete customer/brand pair: {customer!r}, {brand!r}')
        entry = {'mcid': 'MKA_RKA:' + brand, 'mcn': brand,
                 'source_channel': identifier(row[1])}
        if customer in result and result[customer] != entry:
            raise ValueError(f'Conflicting brand assignments for customer {customer}')
        result[customer] = entry
    return dict(sorted(result.items()))


def load_brand_mapping(path: Path) -> dict[str, dict[str, str]]:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True, keep_links=False)
    try:
        ws = wb['客户品牌']
        header = next(ws.iter_rows(min_row=1, max_row=1, max_col=5, values_only=True))
        if list(header[1:5]) != ['渠道', '品牌', '客户编码', '客户描述']:
            raise ValueError('Unexpected customer/brand register schema')
        return brand_mapping(list(ws.iter_rows(min_row=2, max_col=5, values_only=True)))
    finally:
        wb.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--ka-details', type=Path, required=True)
    parser.add_argument('--customer-master', type=Path, required=True)
    args = parser.parse_args()
    mapping = load_brand_mapping(args.ka_details)
    static = Path(__file__).resolve().parents[1] / 'streamlit_html_portal/static'
    old = json.loads((static / 'ka-customer-merge.json').read_text(encoding='utf-8'))
    removed = set(old) - set(mapping)
    if removed:
        raise ValueError(f'Previously mapped customers missing in replacement: {sorted(removed)}')
    metadata = {
        'customer_master': {'name': args.customer_master.name,
                            'sha256': hashlib.sha256(args.customer_master.read_bytes()).hexdigest()},
        'ka_brands': {'name': args.ka_details.name,
                      'sha256': hashlib.sha256(args.ka_details.read_bytes()).hexdigest()},
        'brand_customer_count': len(mapping),
        'new_customer_count': len(set(mapping) - set(old)),
        'changed_customer_count': sum(old[c] != mapping[c] for c in set(old) & set(mapping)),
        'priority': 'explicit KA brand group > current promotion merge > historical fallback',
        'scope': 'same customer/brand grouping for both 2025 and 2026; no metric overrides',
    }
    (static / 'ka-customer-merge.json').write_text(
        json.dumps(mapping, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    (static / 'customer-mapping-sources.json').write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
