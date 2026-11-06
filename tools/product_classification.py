"""Safe product dimensions; numeric business fields are never modified here."""
import json
from pathlib import Path

OVERRIDES_PATH = Path(__file__).resolve().parents[1] / 'streamlit_html_portal/static/product-classification-overrides.json'
OVERRIDES = json.loads(OVERRIDES_PATH.read_text(encoding='utf-8'))
INVALID_LABELS = {'', '#N/A', '#VALUE!', '#REF!', '#DIV/0!', '#NAME?', '#NUM!', '#NULL!',
                  '#SPILL!', '#CALC!', 'NAN', 'NONE', 'NULL', '未映射'}


def product_label(value):
    label = str(value).strip() if value is not None else ''
    return '' if label.upper() in INVALID_LABELS else label


def product_dimensions(material, description, category, item):
    material = product_label(material)
    override = OVERRIDES['materials'].get(material, {})
    return (
        product_label(category) or override.get('category') or '未映射',
        product_label(item) or product_label(description) or material or '未映射',
    )


def repair_product_rows(records):
    repaired = {}
    for row in records:
        old = (row.get('cat'), row.get('item'))
        row['cat'], row['item'] = product_dimensions(
            row.get('pc'), row.get('pn'), *old,
        )
        if old != (row['cat'], row['item']):
            repaired[row.get('pc', '')] = {'name': row.get('pn', ''),
                                          'category': row['cat'], 'item': row['item']}
    return repaired
