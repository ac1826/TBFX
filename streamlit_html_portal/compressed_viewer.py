"""Transport the original gzip bytes; decompress HTML only in the browser."""

import base64
import json

from streamlit_html_portal.customer_yoy import customer_yoy_runtime


def compressed_dashboard_html(compressed: bytes, *, sales: bool = False) -> str:
    payload = base64.b64encode(compressed).decode("ascii")
    runtime = json.dumps(customer_yoy_runtime() if sales else "", ensure_ascii=False).replace("</", "<\\/")
    return """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"></head><body>
<p id="loading" role="status">正在解压并打开看板，请稍候……</p>
<script>
(async () => {
  try {
    if (typeof DecompressionStream === 'undefined') {
      throw new Error('浏览器不支持 gzip 解压，请使用新版 Edge、Chrome 或 Firefox');
    }
    const encoded = '__PAYLOAD__';
    const runtime = __RUNTIME__;
    // Decode in bounded chunks rather than allocating one large binary string.
    const chunks = [];
    for (let offset = 0; offset < encoded.length; offset += 262144) {
      const binary = atob(encoded.slice(offset, offset + 262144));
      chunks.push(Uint8Array.from(binary, char => char.charCodeAt(0)));
    }
    const stream = new Blob(chunks).stream().pipeThrough(new DecompressionStream('gzip'));
    let html = await new Response(stream).text();
    if (runtime) {
      const marker = "    fetch('2026-vs-2025-yoy-dashboard.html').then(response => {";
      const start = html.indexOf(marker);
      const end = start < 0 ? -1 : html.indexOf("    window.addEventListener('resize'", start);
      if (start >= 0 && end >= 0) {
        html = html.slice(0, start) + runtime + html.slice(end);
      } else if (html.includes('customerRankYoyRuntime(')) {
        html = html.replace('</body>', '<script>\\n' + runtime + '<' + '/script>\\n</body>');
      }
    }
    document.open();
    document.write(html);
    document.close();
  } catch (error) {
    document.getElementById('loading').textContent = '看板加载失败：' + error.message;
  }
})();
</script></body></html>
""".replace("__PAYLOAD__", payload).replace("__RUNTIME__", runtime)
