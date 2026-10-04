from __future__ import annotations
import json
from pathlib import Path
import sys
ROOT_DIR=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT_DIR))
from app.rag import Retriever
from app.config import ROOT

# Hand-authored synthetic retrieval benchmark for this portfolio knowledge base.
# It is not a production accuracy claim; it only verifies that common paraphrases
# retrieve the intended knowledge section.
CASES=[
    ('验收为什么必须挂在采购单下面？','01_procurement_receiving:1'),
    ('采购5个先收3个，订单是什么状态？','01_procurement_receiving:2'),
    ('到货数量超过采购数量怎么办？','01_procurement_receiving:3'),
    ('库存余额和库存台账有什么区别？','02_inventory_traceability:1'),
    ('库存流水里至少要记录哪些字段？','02_inventory_traceability:2'),
    ('什么时候需要补货预警？','02_inventory_traceability:3'),
    ('为什么不能库存不够也先发货？','03_sales_shipping:1'),
    ('销售单库存不足时状态怎么处理？','03_sales_shipping:2'),
    ('写库存失败以后订单已经更新怎么办？','03_sales_shipping:3'),
    ('销售角色能不能做采购审批？','04_permissions_uat:1'),
    ('用户验收测试需要覆盖哪些情况？','04_permissions_uat:2'),
    ('Fit-Gap分析不能只写缺功能还要做什么？','05_fit_gap_method:1'),
    ('这个项目能不能说自己做过SAP上线？','05_fit_gap_method:2'),
]

def main():
    r=Retriever(); rows=[]; rr=0.0
    for q,expected in CASES:
        hits=r.search(q,3); ids=[h['chunk_id'] for h in hits]
        rank=(ids.index(expected)+1) if expected in ids else None
        rr += 1/rank if rank else 0
        rows.append({'question':q,'expected_chunk':expected,'top_chunks':ids,'rank':rank,'hit_at_1':rank==1,'hit_at_3':rank is not None})
    n=len(rows); report={
        'evaluation_type':'hand-authored synthetic retrieval regression; not production RAG accuracy',
        'n':n,'recall_at_1':sum(x['hit_at_1'] for x in rows)/n,
        'recall_at_3':sum(x['hit_at_3'] for x in rows)/n,
        'mrr':rr/n,'cases':rows
    }
    out=ROOT/'outputs'/'rag_evaluation.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# RAG检索回归评测','',f"- 类型：{report['evaluation_type']}",f"- 案例：{n}",f"- Recall@1：{report['recall_at_1']:.1%}",f"- Recall@3：{report['recall_at_3']:.1%}",f"- MRR：{report['mrr']:.3f}",'', '> 注意：这是本项目知识库上的合成检索回归，用于验证常见改写能否命中预期章节，不代表生产RAG效果。','', '|问题|期望Chunk|排名|Top3|','|---|---|---:|---|']
    for x in rows: md.append(f"|{x['question']}|{x['expected_chunk']}|{x['rank'] or '-'}|{', '.join(x['top_chunks'])}|")
    (ROOT/'outputs'/'rag_evaluation_report.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['recall_at_3']==1 else 1)
if __name__=='__main__': main()
