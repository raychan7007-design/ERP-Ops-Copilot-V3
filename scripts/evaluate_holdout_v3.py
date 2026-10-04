from __future__ import annotations
import hashlib,json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from app.db import rebuild_demo_db
from app.copilot import ask

EVAL=ROOT/'evaluation'
OUT=ROOT/'outputs'/'holdout_evaluation_v3.json'
REPORT=ROOT/'outputs'/'holdout_evaluation_v3_report.md'

def get_path(obj,path):
    cur=obj
    for part in path.split('.'):
        if isinstance(cur,list): cur=cur[int(part)]
        else: cur=cur[part]
    return cur

def all_text(r):
    return ' '.join([str(r.get('answer','')),str(r.get('reason','')),str(r.get('action','')),json.dumps(r,ensure_ascii=False)])

def check(assertion,result):
    t=assertion['type']
    if t=='contains':
        ok=assertion['value'] in all_text(result); actual='present' if ok else 'missing'
    elif t=='field':
        try: actual=get_path(result,assertion['path']); ok=actual==assertion['equals']
        except Exception as e: actual=f'ERROR:{type(e).__name__}'; ok=False
    elif t=='list_min':
        try: actual=len(get_path(result,assertion['path'])); ok=actual>=assertion['min']
        except Exception as e: actual=f'ERROR:{type(e).__name__}'; ok=False
    elif t=='evidence_chunk':
        ids=[x.get('chunk_id') for x in (result.get('evidence') or []) if isinstance(x,dict)]
        actual=ids; ok=assertion['value'] in ids
    elif t=='case_kind':
        kinds=[x.get('kind') for x in ((result.get('uat') or {}).get('cases') or [])]
        actual=kinds; ok=assertion['value'] in kinds
    else:
        actual='unknown assertion'; ok=False
    return {'assertion':assertion,'actual':actual,'pass':ok}

def main():
    if OUT.exists():
        raise SystemExit('Refusing to rerun sealed V3 holdout while output exists')
    protocol=json.loads((EVAL/'holdout_protocol_v3.json').read_text(encoding='utf-8'))
    raw=(EVAL/'holdout_cases_v3.json').read_bytes()
    digest=hashlib.sha256(raw).hexdigest()
    if digest!=protocol['sha256']: raise SystemExit('Holdout hash mismatch; dataset is not the frozen version')
    payload=json.loads(raw.decode('utf-8'))
    rebuild_demo_db()
    rows=[]
    for case in payload['cases']:
        result=ask(case['question'])
        route_pass=result.get('route')==case['route']
        assertions=[check(a,result) for a in case.get('assertions',[])]
        ok=route_pass and all(x['pass'] for x in assertions)
        rows.append({'id':case['id'],'question':case['question'],'expected_route':case['route'],'actual_route':result.get('route'),'route_pass':route_pass,'assertions':assertions,'pass':ok})
    passed=sum(x['pass'] for x in rows); n=len(rows)
    route_passed=sum(x['route_pass'] for x in rows)
    assertion_total=sum(len(x['assertions']) for x in rows); assertion_passed=sum(a['pass'] for x in rows for a in x['assertions'])
    report={
        'evaluation_type':protocol['evaluation_type'],
        'dataset_sha256':digest,'n':n,'passed':passed,'failed':n-passed,'case_pass_rate':passed/n,
        'route_passed':route_passed,'route_accuracy':route_passed/n,
        'assertions_passed':assertion_passed,'assertions_total':assertion_total,
        'assertion_pass_rate':assertion_passed/assertion_total if assertion_total else None,
        'cases':rows
    }
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    md=['# V3 封存 Holdout 评测','',f"- 类型：{report['evaluation_type']}",f"- 数据集 SHA256：`{digest}`",f"- Case：{passed}/{n} 通过（{passed/n:.1%}）",f"- Router：{route_passed}/{n}（{route_passed/n:.1%}）",f"- 结构/内容断言：{assertion_passed}/{assertion_total}（{assertion_passed/assertion_total:.1%}）",'', '> 这是开发验证完成后才执行的合成封存测试，不是生产准确率、真实用户效果或独立第三方评测。首次执行后不据此修改V3代码；失败项原样保留。','', '|ID|问题|期望路由|实际路由|结果|','|---|---|---|---|---|']
    for x in rows: md.append(f"|{x['id']}|{x['question']}|{x['expected_route']}|{x['actual_route']}|{'PASS' if x['pass'] else 'FAIL'}|")
    fails=[x for x in rows if not x['pass']]
    if fails:
        md += ['','## 失败明细','']
        for x in fails:
            md.append(f"### {x['id']} {x['question']}")
            md.append(f"- 路由：期望 `{x['expected_route']}`，实际 `{x['actual_route']}`")
            for a in x['assertions']:
                if not a['pass']: md.append(f"- 断言失败：`{json.dumps(a['assertion'],ensure_ascii=False)}`；实际：`{a['actual']}`")
    REPORT.write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False,indent=2))
    raise SystemExit(0 if passed==n else 2)

if __name__=='__main__': main()
