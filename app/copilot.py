from __future__ import annotations
from .router import route_with_reason
from .diagnostics import diagnose_purchase,diagnose_sales
from .sql_tools import get_stock,recent_movements,stock_summary,ERPDataNotFound,explain_tool
from .rag import answer_from_knowledge
from .uat import generate_uat

def ask(question:str,db_path=None):
    if not question or not question.strip():
        raise ValueError('question must be non-empty')
    kind,ent,route_trace=route_with_reason(question)
    kw={} if db_path is None else {'db_path':db_path}
    try:
        if kind=='purchase_diagnosis':
            result=diagnose_purchase(ent['po_id'],**kw)
        elif kind=='sales_diagnosis':
            result=diagnose_sales(ent['so_id'],**kw)
        elif kind=='sku_query':
            stock=get_stock(ent['sku'],**kw); moves=recent_movements(ent['sku'],**kw)
            result={"type":"sku_query","record":stock,"recent_movements":moves,
                    "answer":f"{stock['sku']} 当前库存{stock['stock_qty']}件，安全库存{stock['safety_stock']}件，库存状态={'低于安全库存' if stock['below_safety_stock'] else '正常'}。",
                    "evidence":{"source":"SQL"},
                    "tool_trace":[explain_tool('get_stock',{'sku':ent['sku']}),explain_tool('recent_movements',{'sku':ent['sku'],'limit':5})]}
        elif kind=='stock_summary':
            rows=stock_summary(**kw); result={"type":"stock_summary","rows":rows,"answer":"；".join(f"{r['sku']}={r['stock_qty']}({r['stock_health']})" for r in rows),"evidence":{"source":"SQL"},
                    "tool_trace":[explain_tool('stock_summary')]}
        elif kind=='uat':
            uat=generate_uat(question)
            result={"type":"uat","answer":f"已按{len(uat['cases'])}个场景覆盖正常、边界、异常/权限和一致性维度。","uat":uat,"evidence":{"source":"规则模板"},
                    "tool_trace":[{"tool":"uat_generator","purpose":"将需求拆成可执行验收场景","method":"deterministic rule template"}]}
        else:
            rag=answer_from_knowledge(question); result={"type":"knowledge","answer":rag['answer'],"evidence":rag['evidence'],"confidence":rag['confidence'],"retrieval_trace":rag['retrieval_trace'],
                    "tool_trace":[{"tool":"knowledge_retriever","purpose":"从ERP知识库检索可引用规则","method":"local TF-IDF-like cosine + domain query expansion"}]}
    except ERPDataNotFound as exc:
        result={"type":kind,"answer":f"未找到业务对象：{exc.args[0]}。请核对单据或SKU编号。","evidence":[],"tool_trace":[]}
    result['route']=kind; result['entities']=ent; result['question']=question; result['route_trace']=route_trace
    return result
