import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_customer_tooltip_yoy_respects_filters_and_distinct_skus():
    import gzip
    html = gzip.decompress((ROOT / 'streamlit_html_portal/static/2026-sales-dashboard.html.gz').read_bytes()).decode('utf-8')
    aggregation = html[html.index('    function sumRows('):html.index('    function topBy(')]
    rate = html[html.index('    function netMarginRate('):html.index('    function metricValue(')]
    script = r'''
const {customerRankYoyRuntime, customerRankYoyData, withCustomerRankYoy} = require('./tools/customer_rank_yoy.js');
const filters = {monthFilter:['2026.01'],categoryFilter:['A'],channelFilter:['KA'],regionFilter:['华东区']};
const getMultiValues = id => filters[id];
const document = {getElementById:id=>({value:id==='itemFilter'?'__ALL__':''})};
const activeMetric = 'income_k';
const currentScopeRows = rows => rows.filter(r=>r.p==='上海市');
const topBy = rows => rows.sort((a,b)=>b.income_k-a.income_k);
const base={mcid:'C',mcn:'客户',pc:'sku1',cat:'A',ch:'KA',nr:'华东区',p:'上海市',ct:'上海',mo:'1月',v:10,inc:100,nm:20,ni:100,ad:0};
const prior=[base,{...base,v:10,inc:100,nm:20},{...base,mo:'2月',inc:9000}, {...base,p:'北京市',inc:9000}, {...base,cat:'B',inc:9000}];
const now=[{...base,v:30,inc:300,nm:90,ni:300,mo:'2026.01'}];
const currentRows=()=>now;
let formatter;
const charts={customerRank:{getOption:()=>({tooltip:[{formatter:()=> '客户<br/>销量：30<br/>销额：300<br/>净边贡：90<br/>净边贡率：30.0%<br/>SKU数：1'}]}),setOption:option=>{formatter=option.tooltip.formatter;}}};
function renderCustomerRank(){}
''' + rate + aggregation + r'''
customerRankYoyRuntime(prior);
const result=formatter([{dataIndex:0}]);
if(!result.includes('销量：30　同比：+50.0%'))throw Error(result);
if(!result.includes('销额：300　同比：+50.0%'))throw Error(result);
if(!result.includes('净边贡：90　同比：+125.0%'))throw Error(result);
if(!result.includes('净边贡率：30.0%　同比：+10.0%'))throw Error(result);
if(!result.includes('SKU数：1　同比：+0.0%'))throw Error(result);
// The Streamlit portal ships a compact aggregated baseline.  It must use the
// same tooltip path instead of throwing when Array#filter is unavailable.
customerRankYoyRuntime({aggregated:true,rows:[{mcid:'C',mcn:'客户',volume_ton:20,income_k:200,net_margin_k:40,net_margin_rate:0.2,sku_cnt:1}]});
const compactResult=formatter([{dataIndex:0}]);
if(!compactResult.includes('销额：300　同比：—'))throw Error('Aggregate must not substitute for monthly baseline');
customerRankYoyRuntime(prior);
filters.monthFilter=['2026.02'];renderCustomerRank(now);
if(!formatter([{dataIndex:0}]).includes('2025为0，无法计算')) {
  // February has a nonzero sales baseline and must not use January values.
  if(!formatter([{dataIndex:0}]).includes('同比：-96.7%'))throw Error('Month filter ignored');
}
filters.monthFilter=['2026.03'];renderCustomerRank(now);
if((formatter([{dataIndex:0}]).match(/2025无数据/g)||[]).length!==5)throw Error('Missing prior-year state');
filters.monthFilter=['2025.01'];renderCustomerRank([{...now[0],mo:'2025.01'}]);
if((formatter([{dataIndex:0}]).match(/同比：—/g)||[]).length!==5)throw Error('2025 must not compare against itself');
filters.monthFilter=['2026.01'];
customerRankYoyRuntime(prior.map(r=>({...r,mo:`2025.${String(parseInt(r.mo)).padStart(2,'0')}`})));
if(!formatter([{dataIndex:0}]).includes('销额：300　同比：+50.0%'))throw Error('Portal month labels ignored');
filters.monthFilter=['2026.01','2026.02'];renderCustomerRank(now);
if(!formatter([{dataIndex:0}]).includes('同比：-96.7%'))throw Error('Multi-month prior selection ignored');
const priorHtml='const APP_DATA = '+JSON.stringify({records:[{...base,y:'2025'},{...base,y:'2026'}]})+';\n';
if(customerRankYoyData(priorHtml).length!==1)throw Error('Wrong year');
const patched=withCustomerRankYoy('<body></body>',[{...base,mcn:'</script>'}]);
if(patched.includes('"mcn":"</script>"'))throw Error('Unescaped script data');
console.log(JSON.stringify({result}));
'''
    subprocess.check_output(['node', '-e', script], cwd=ROOT, text=True, encoding='utf-8')
