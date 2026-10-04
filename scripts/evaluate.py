from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT_DIR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT_DIR))
from app.db import rebuild_demo_db
from app.copilot import ask
from app.config import ROOT

CASES=[
('PO100为什么还是部分验收？','purchase_diagnosis','剩余2件'),
('PO102为什么还在待验收？','purchase_diagnosis','累计验收0件'),
('SO100为什么不能出库？','sales_diagnosis','库存不足'),
('SO102现在能不能出库？','sales_diagnosis','库存满足'),
('SKU001库存多少？','sku_query','当前库存3件'),
('SKU003库存多少？','sku_query','当前库存0件'),
('给我看库存汇总和安全库存','stock_summary','SKU001=3'),
('为什么库存余额还需要库存流水？','knowledge','库存余额'),
('验收为什么必须关联采购订单？','knowledge','采购订单'),
('Fit-Gap分析之后还要做什么？','knowledge','AS-IS'),
('销售库存不足怎么处理？','knowledge','销售订单'),
('采购和销售角色为什么要分权限？','knowledge','采购'),
('分批验收怎么做UAT？','uat','UAT'),
('库存不足出库怎么设计测试用例？','uat','UAT'),
('权限功能如何验收？','uat','UAT'),
('SO999为什么不能出库？','sales_diagnosis','未找到业务对象'),
('PO999状态是什么？','purchase_diagnosis','未找到业务对象'),
]

def text_of(r):
    parts=[str(r.get('answer','')),str(r.get('reason','')),json.dumps(r.get('uat',{}),ensure_ascii=False)]
    return ' '.join(parts)

def main():
    rebuild_demo_db(); rows=[]
    for q,route,needle in CASES:
        r=ask(q); ok_route=r.get('route')==route; ok_content=needle in text_of(r)
        rows.append({'question':q,'expected_route':route,'actual_route':r.get('route'),'route_pass':ok_route,'content_assertion':needle,'content_pass':ok_content,'pass':ok_route and ok_content})
    passed=sum(x['pass'] for x in rows); report={'evaluation_type':'fixed synthetic functional regression; not model accuracy or production benchmark','n':len(rows),'passed':passed,'failed':len(rows)-passed,'pass_rate':passed/len(rows),'cases':rows}
    out=ROOT/'outputs'/'evaluation.json'; out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if passed==len(rows) else 1)
if __name__=='__main__': main()
