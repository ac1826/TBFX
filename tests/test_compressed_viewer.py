import gzip
import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit_html_portal.compressed_viewer import compressed_dashboard_html
from streamlit_html_portal.customer_yoy import inject_customer_yoy


@pytest.mark.parametrize("sales", [False, True])
def test_browser_decompression_preserves_html(sales):
    source = (
        '<html><body>客户数据：销量 123.456，合并客户保持不变<script>\n'
        '    fetch(\'2026-vs-2025-yoy-dashboard.html\').then(response => {\n'
        '    window.addEventListener(\'resize\', () => {});\n'
        '</script></body></html>'
    )
    wrapper = compressed_dashboard_html(gzip.compress(source.encode()), sales=sales)
    script = wrapper.split('<script>', 1)[1].rsplit('</script>', 1)[0]
    harness = "const document={open(){},write(html){process.stdout.write(JSON.stringify(html));},close(){},getElementById(){throw Error('Loader failed');}};\n"
    result = subprocess.check_output(['node', '-e', harness + script], text=True, encoding='utf-8')
    assert json.loads(result) == (inject_customer_yoy(source) if sales else source)


def test_missing_decompression_support_shows_error():
    wrapper = compressed_dashboard_html(gzip.compress(b'<body>unchanged</body>'))
    script = wrapper.split('<script>', 1)[1].rsplit('</script>', 1)[0]
    harness = "global.DecompressionStream=undefined; const document={getElementById(){return {set textContent(text){console.log(text)}}}};\n"
    result = subprocess.check_output(['node', '-e', harness + script], text=True, encoding='utf-8')
    assert '浏览器不支持 gzip 解压' in result
