// Customer summary uses the existing sales detail (no second data payload).
function customerSummaryData(rows, selectedPeriods, availablePeriods, getPriorRows) {
  const latestYear = availablePeriods.at(-1)?.slice(0, 4);
  const periods = selectedPeriods.length ? [...selectedPeriods].sort() :
    availablePeriods.filter(period => period.startsWith(latestYear + '.'));
  const periodSet = new Set(periods);
  const priorPeriods = periods.map(period => String(Number(period.slice(0, 4)) - 1) + period.slice(4));
  const available = new Set(availablePeriods);
  const comparable = priorPeriods.length > 0 && priorPeriods.every(period => available.has(period));
  const collect = source => {
    const groups = new Map();
    for (const row of source) {
      if (!row.mcid) continue;
      let customer = groups.get(row.mcid);
      if (!customer) {
        customer = {id:row.mcid, name:row.mcn || row.mcid, period:'', sales:0, margin:0, base:0,
          ka:row.mcid.startsWith('MKA_RKA:'), distributor:false, ecommerce:false};
        groups.set(row.mcid, customer);
      }
      if (row.mo >= customer.period && row.mcn) {
        customer.name = row.mcn;
        customer.period = row.mo;
      }
      customer.sales += Number(row.inc || 0);
      customer.margin += Number(row.nm || 0);
      customer.base += Number(row.ni || 0) - Number(row.ad || 0);
      customer.ka ||= row.ch === 'KA';
      customer.ecommerce ||= row.ch === '电商';
      customer.distributor ||= Boolean(row.ch && !['KA','电商','未映射'].includes(row.ch));
    }
    return groups;
  };
  const rate = customer => customer && Math.abs(customer.base) > 1e-10 ? customer.margin / customer.base : null;
  const growth = (now, before) => Math.abs(before) > 1e-10 ? (now - before) / Math.abs(before) : null;
  const current = collect(rows.filter(row => periodSet.has(row.mo)));
  const prior = comparable ? collect(getPriorRows(priorPeriods)) : new Map();
  const top = [...current.values()].filter(customer => customer.sales > 0)
    .sort((a,b) => b.sales - a.sales || a.id.localeCompare(b.id)).slice(0,20).map(customer => {
      const baseline = prior.get(customer.id);
      const currentRate = rate(customer);
      const priorRate = rate(baseline);
      return {
        name:customer.name,
        type:customer.ka ? 'KA' : customer.distributor ? '经销' : customer.ecommerce ? '电商' : '—',
        sales:customer.sales, salesYoy:growth(customer.sales, baseline?.sales),
        margin:customer.margin, marginYoy:growth(customer.margin, baseline?.margin),
        rate:currentRate, rateYoy:currentRate === null || priorRate === null ? null : currentRate - priorRate
      };
    });
  return {top, periods, priorPeriods:comparable ? priorPeriods : [], defaultPeriod:!selectedPeriods.length};
}

function customerSummaryRuntime() {
  const wrap = document.querySelector('.wrap');
  if (!wrap || document.getElementById('customer-summary')) return;
  const section = document.createElement('section');
  section.id = 'customer-summary';
  section.className = 'panel customer-summary';
  section.setAttribute('aria-labelledby', 'customer-summary-title');
  section.innerHTML = `
    <div class="panel-head">
      <h2 id="customer-summary-title">前20大客户信息汇总</h2>
      <span class="panel-note">按销额排名 · 金额：千元 · pp：百分点</span>
    </div>
    <p class="customer-summary-period" role="status"></p>
    <p class="customer-summary-scroll-note">横向滑动查看全部指标</p>
    <div class="table-wrap customer-summary-scroll" tabindex="0" role="region" aria-labelledby="customer-summary-title">
      <table aria-labelledby="customer-summary-title">
        <thead><tr>
          <th scope="col">排名</th><th scope="col">客户名称</th><th scope="col">类型</th>
          <th scope="col">销额</th><th scope="col">销额同比</th>
          <th scope="col">净边贡</th><th scope="col">净边贡同比</th>
          <th scope="col">净边贡率</th><th scope="col">净边贡率同比</th>
        </tr></thead>
        <tbody></tbody>
      </table>
    </div>`;
  const style = document.createElement('style');
  style.textContent = `
    .customer-summary { min-width:0; }
    .customer-summary .panel-head { flex-wrap:wrap; align-items:baseline; }
    .customer-summary .panel-note { text-align:left; }
    .customer-summary-period { margin:8px 0 12px; color:var(--muted); font-size:13px; line-height:1.5; }
    .customer-summary-scroll { max-height:none; }
    .customer-summary-scroll:focus-visible { outline:2px solid var(--accent); outline-offset:2px; }
    .customer-summary table { min-width:820px; font-variant-numeric:tabular-nums; }
    .customer-summary :is(th,td):nth-child(n+4) { text-align:right; }
    .customer-summary :is(th,td):first-child { text-align:center; width:48px; color:var(--muted); }
    .customer-summary tbody th { position:static; background:transparent; color:var(--text);
      font-weight:600; white-space:normal; min-width:145px; max-width:300px; }
    .customer-summary tbody tr:nth-child(even) { background:#f8fafc; }
    .customer-summary tbody tr:hover { background:#eef8f8; }
    .customer-summary .customer-type { display:inline-block; padding:2px 7px; border-radius:4px;
      background:#eef2f7; color:#475569; font-size:12px; }
    .customer-summary .customer-type-ka { background:#e5f5ef; color:#086656; }
    .customer-summary .customer-empty { text-align:center !important; padding:24px; }
    .customer-summary .negative { color:#b4232c; }
    .customer-summary-scroll-note { display:none; margin:0 0 8px; font-size:12px; color:var(--muted); }
    @media (max-width:920px) {
      .customer-summary-scroll-note { display:block; }
      .customer-summary table { table-layout:fixed; }
      .customer-summary :is(th,td) { padding-inline:7px; }
      .customer-summary thead th:nth-child(1) { width:38px; }
      .customer-summary thead th:nth-child(2) { width:126px; }
      .customer-summary thead th:nth-child(3) { width:48px; }
      .customer-summary thead th:nth-child(4) { width:78px; }
      .customer-summary tbody th { min-width:0; overflow-wrap:anywhere; }
    }
  `;
  document.head.append(style);
  wrap.append(section);
  const periodLabel = section.querySelector('.customer-summary-period');
  const body = section.querySelector('tbody');
  const money = new Intl.NumberFormat('zh-CN', {maximumFractionDigits:0});
  const describe = periods => {
    const byYear = new Map();
    periods.forEach(period => {
      const [year, month] = period.split('.');
      if (!byYear.has(year)) byYear.set(year, []);
      byYear.get(year).push(Number(month));
    });
    return [...byYear].map(([year, months]) => {
      const first = months[0], last = months.at(-1);
      return year + '年' + (months.length > 1 && last - first + 1 === months.length ?
        first + '–' + last : months.join('、')) + '月';
    }).join('；');
  };
  const priorRows = periods => {
    const months = new Set(periods);
    const cats = getMultiValues('categoryFilter');
    const channels = getMultiValues('channelFilter');
    const regions = getMultiValues('regionFilter');
    const item = document.getElementById('itemFilter').value;
    const kw = document.getElementById('searchInput').value.trim().toLowerCase();
    return currentScopeRows(RAW.filter(r =>
      months.has(r.mo) && (!cats.length || cats.includes(r.cat)) &&
      (item === '__ALL__' || r.item === item) &&
      (!channels.length || channels.includes(r.ch)) && (!regions.length || regions.includes(r.nr)) &&
      (!kw || `${r.pc} ${r.pn} ${r.cn} ${r.cid} ${r.mcn} ${r.mcid} ${r.o} ${r.nr}`.toLowerCase().includes(kw))
    ));
  };
  function draw(rows) {
    const data = customerSummaryData(currentScopeRows(rows), getMultiValues('monthFilter'), MONTH_ORDER, priorRows);
    periodLabel.textContent = (data.defaultPeriod ? '默认：' : '所选期间：') + describe(data.periods) +
      ' · ' + currentScopeLabel() + (data.priorPeriods.length ?
        ' · 同比：' + describe(data.priorPeriods) : ' · 无完整上年同期') +
      ' · — 表示无可比值';
    const add = (tr, value, {header=false, className=''} = {}) => {
      const cell = document.createElement(header ? 'th' : 'td');
      if (header) cell.scope = 'row';
      cell.textContent = value;
      cell.className = className;
      tr.append(cell);
      return cell;
    };
    const delta = (tr, value, suffix) => {
      if (value === null) { add(tr, '—'); return; }
      const rounded = Number((value * 100).toFixed(1));
      add(tr, (rounded > 0 ? '+' : '') + rounded.toFixed(1) + suffix,
        {className:rounded > 0 ? 'positive' : rounded < 0 ? 'negative' : ''});
    };
    const fragment = document.createDocumentFragment();
    data.top.forEach((customer,index) => {
      const tr = document.createElement('tr');
      add(tr, String(index + 1).padStart(2,'0'));
      add(tr, customer.name, {header:true});
      const type = document.createElement('span');
      type.className = 'customer-type' + (customer.type === 'KA' ? ' customer-type-ka' : '');
      type.textContent = customer.type;
      add(tr, '').append(type);
      add(tr, money.format(customer.sales)); delta(tr, customer.salesYoy, '%');
      add(tr, money.format(customer.margin)); delta(tr, customer.marginYoy, '%');
      add(tr, customer.rate === null ? '—' : (customer.rate * 100).toFixed(1) + '%');
      delta(tr, customer.rateYoy, ' pp');
      fragment.append(tr);
    });
    if (!data.top.length) {
      const tr = document.createElement('tr');
      add(tr, '当前筛选没有可排名的客户销额。', {className:'customer-empty'}).colSpan = 9;
      fragment.append(tr);
    }
    body.replaceChildren(fragment);
  }
  const previous = renderCustomerRank;
  renderCustomerRank = function(rows) {
    previous(rows);
    draw(rows);
  };
  draw(currentRows());
}

if (typeof module !== 'undefined') module.exports = {customerSummaryData};
