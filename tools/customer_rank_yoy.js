// Apply the same tooltip enhancement to the standalone and encrypted dashboards.
function customerRankYoyRuntime(priorRows) {
  const originalRenderCustomerRank = renderCustomerRank;
  renderCustomerRank = function(rows) {
    originalRenderCustomerRank(rows);
    const months = getMultiValues('monthFilter').map(m => `${parseInt(String(m).split('.').pop(), 10)}月`);
    const cats = getMultiValues('categoryFilter');
    const channels = getMultiValues('channelFilter');
    const regions = getMultiValues('regionFilter');
    const item = document.getElementById('itemFilter').value;
    const kw = document.getElementById('searchInput').value.trim().toLowerCase();
    const filteredPrior = priorRows.filter(r =>
      (!months.length || months.includes(r.mo)) &&
      (!cats.length || cats.includes(r.cat)) &&
      (item === '__ALL__' || r.item === item) &&
      (!channels.length || channels.includes(r.ch)) &&
      (!regions.length || regions.includes(r.nr)) &&
      (!kw || `${r.pc} ${r.pn} ${r.mcn} ${r.mcid} ${r.o} ${r.nr}`.toLowerCase().includes(kw))
    );
    const prior = priorRows && priorRows.aggregated
      ? new Map((priorRows.rows || []).map(r => [r.mcid, r]))
      : new Map(groupBy(currentScopeRows(filteredPrior), ['mcid']).map(r => [r.mcid, r]));
    const current = topBy(groupBy(currentScopeRows(rows), ['mcid']), activeMetric, 20).reverse();
    const keys = ['volume_ton', 'income_k', 'net_margin_k', 'net_margin_rate', 'sku_cnt'];
    const display = (value, key) => typeof fmt === 'function' ? fmt(value, key) : key === 'net_margin_rate' ? `${(Number(value || 0) * 100).toFixed(1)}%` : Number(value || 0).toLocaleString('zh-CN');
    const change = (now, before, rate) => {
      if (rate) {
        const delta = (now - before) * 100;
        return `${delta >= 0 ? '+' : ''}${delta.toFixed(1)}%`;
      }
      if (!before) return now ? '2025为0，无法计算' : '0.0%';
      const delta = (now - before) / Math.abs(before) * 100;
      return `${delta >= 0 ? '+' : ''}${delta.toFixed(1)}%`;
    };
    charts.customerRank.setOption({ tooltip:{ formatter:params => {
      const r = current[params[0].dataIndex] || {};
      const old = prior.get(r.mcid);
      const value = key => old ? change(r[key], old[key], key === 'net_margin_rate') : '2025无数据';
      return `${r.customerName || r.mcn || r.mcid || params[0].name}<br/>` +
        `销量：${display(r.volume_ton,'volume_ton')}　同比：${value('volume_ton')}<br/>` +
        `销额：${display(r.income_k,'income_k')}　同比：${value('income_k')}<br/>` +
        `净边贡：${display(r.net_margin_k,'net_margin_k')}　同比：${value('net_margin_k')}<br/>` +
        `净边贡率：${display(r.net_margin_rate,'net_margin_rate')}　同比：${value('net_margin_rate')}<br/>` +
        `SKU数：${(r.sku_cnt || 0).toLocaleString('zh-CN')}　同比：${value('sku_cnt')}`;
    } } }, true);
  };
  renderCustomerRank(currentRows());
}

function customerRankYoyData(html) {
  const marker = 'const APP_DATA = ';
  const start = html.indexOf(marker);
  if (start < 0) throw new Error('Missing dashboard data');
  const end = html.indexOf(';\n', start);
  if (end < 0) throw new Error('Missing dashboard data terminator');
  return JSON.parse(html.slice(start + marker.length, end)).records.filter(r => r.y === '2025');
}

function withCustomerRankYoy(html, priorRows) {
  const data = JSON.stringify(priorRows).replace(/</g, '\\u003c');
  const script = '<script>(' + customerRankYoyRuntime.toString() + ')(' + data + ');<\/script>';
  return html.replace('</body>', script + '\n</body>');
}

if (typeof module !== 'undefined') module.exports = { customerRankYoyRuntime, customerRankYoyData, withCustomerRankYoy };
