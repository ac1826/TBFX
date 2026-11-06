import json

import pytest

from tools.update_customer_brands import brand_mapping
from tools.update_dashboard_data import (
    CUSTOMER_MASTER_NAME, KA_CUSTOMER_MERGE_SUPPLEMENT, promotion_customer_merges,
    supplement_customer_merges,
)


def test_current_customer_master_and_brand_groups():
    assert CUSTOMER_MASTER_NAME == '10月客户明细及合并.xlsx'
    mapping = json.loads(KA_CUSTOMER_MERGE_SUPPLEMENT.read_text(encoding='utf-8'))
    assert len(mapping) == 390
    for customer in ['279720', '279805', '279849']:
        assert mapping[customer]['mcn'] == 'N多'
    assert mapping['262910']['mcn'] == '河南淘小胖'
    assert mapping['261172']['mcn'] == '开市客烘焙工厂'
    assert mapping['GE18']['mcn'] == '意曼多'


def test_reject_conflicting_or_incomplete_brand_assignments():
    with pytest.raises(ValueError, match='Conflicting'):
        brand_mapping([(None, 'KA', 'A', '1'), (None, 'KA', 'B', '1')])
    with pytest.raises(ValueError, match='Incomplete'):
        brand_mapping([(None, 'KA', 'A', None)])
    assert len(brand_mapping([(None, 'KA', 'A', '1'), (None, 'KA', 'A', '1')])) == 1


def test_current_promotion_merges_override_historical_fallbacks():
    latest = promotion_customer_merges([
        {'客户编码': '1', '合并-促销': '1'},
        {'客户编码': '2', '合并-促销': '3'},
    ])
    assert supplement_customer_merges(latest, {'1': {'mcid': '9'}}) == {'1': '1', '2': '3'}
    with pytest.raises(ValueError, match='Conflicting promotion'):
        promotion_customer_merges([
            {'客户编码': '1', '合并-促销': '2'},
            {'客户编码': '1', '合并-促销': '3'},
        ])
