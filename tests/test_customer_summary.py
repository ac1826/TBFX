import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_sales_customer_summary_comparison_and_weighted_rate():
    script = r"""
const assert = require('node:assert/strict');
const {customerSummaryData} = require('./tools/customer_summary.js');
const months = ['2025.07','2025.08','2026.07','2026.08'];
const sales = (mo, mcid, inc, nm, ni, ad=0, ch='休闲') => ({mo,mcid,mcn:mcid,inc,nm,ni,ad,ch});
const rows = [
  sales('2025.07','MKA_RKA:A',100,15,85,10), sales('2025.08','MKA_RKA:A',50,3,35,5),
  sales('2025.07','B',250,10,200),
  sales('2026.07','MKA_RKA:A',60,12,55,5), sales('2026.07','MKA_RKA:A',140,18,110,10),
  sales('2026.08','MKA_RKA:A',100,20,100,0),
  sales('2026.07','B',210,0,0),
  sales('2026.08','new',10,3,9),
  sales('2026.07','',9999,3,9), sales('2026.07','return',-10,-3,-9)
];
const prior = m => rows.filter(r=>m.includes(r.mo));
let all = customerSummaryData(rows,[],months,prior);
assert.deepEqual(all.periods,['2026.07','2026.08']);
assert.deepEqual(all.priorPeriods,['2025.07','2025.08']);
assert.deepEqual(all.top.map(r=>r.name),['MKA_RKA:A','B','new']);
assert.equal(all.top[0].type,'KA');
assert.equal(all.top[0].salesYoy,1);
assert.equal(all.top[0].rate,0.2);
assert.ok(Math.abs(all.top[0].rateYoy - (0.2 - 18/105)) < 1e-10);
assert.equal(all.top[1].rate,null);
assert.equal(all.top[2].salesYoy,null);
let july = customerSummaryData(rows,['2026.07'],months,prior);
assert.equal(july.top[0].name,'B');
assert.equal(july.top[1].sales,200);
assert.equal(july.top[1].salesYoy,1);
let historical = customerSummaryData(rows,['2025.07'],months,()=>{ throw Error('no 2024'); });
assert.equal(historical.top[0].sales,250);
assert.equal(historical.top[0].salesYoy,null);
assert.deepEqual(historical.priorPeriods,[]);
let mixed = customerSummaryData(rows,['2025.07','2026.08'],months,()=>{throw Error('partial baseline');});
assert.equal(mixed.top[0].sales,250);
assert.equal(mixed.top[0].salesYoy,null);
assert.equal(customerSummaryData([],['2026.07'],months,prior).top.length,0);
assert.equal(customerSummaryData(rows,['2026.07'],months,()=>[]).top[0].salesYoy,null);
"""
    subprocess.run(["node", "-e", script], cwd=ROOT, check=True)
