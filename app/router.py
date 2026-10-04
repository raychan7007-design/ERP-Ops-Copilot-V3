from __future__ import annotations
import re

PO_RE=re.compile(r'(?<![A-Za-z0-9])PO\s*[-_]?\s*(\d+)(?!\d)',re.I)
SO_RE=re.compile(r'(?<![A-Za-z0-9])SO\s*[-_]?\s*(\d+)(?!\d)',re.I)
SKU_RE=re.compile(r'(?<![A-Za-z0-9])SKU\s*[-_]?\s*(\d+)(?!\d)',re.I)

def _norm(prefix,m):
    if not m:return None
    digits=m.group(1)
    return prefix+digits.zfill(3) if len(digits)<3 else prefix+digits

def extract_entities(text:str):
    return {"po_id":_norm('PO',PO_RE.search(text)),"so_id":_norm('SO',SO_RE.search(text)),"sku":_norm('SKU',SKU_RE.search(text))}

def route_with_reason(text:str):
    """Return route, entities and a transparent routing trace.

    The router is intentionally rule based so an interviewer can inspect why a
    question was sent to RAG, SQL, diagnostics or UAT instead of relying on an
    opaque classifier.
    """
    t=text.lower(); ent=extract_entities(text)
    checks=[]
    def hit(name,condition,route_name,reason):
        checks.append({"rule":name,"matched":bool(condition)})
        if condition:
            return route_name,{"matched_rule":name,"reason":reason,"checks":checks.copy()}
        return None

    for args in [
        ('uat_keywords', any(k in t for k in ['uat','测试用例','验收用例','测试场景','需求怎么测','如何验收']), 'uat', '问题包含测试/验收意图，进入UAT辅助。'),
        ('sales_order_diagnosis', bool(ent['so_id']) and any(k in t for k in ['为什么','不能','能不能','出库','状态','异常','诊断','库存']), 'sales_diagnosis', '识别到销售订单号且问题涉及状态、库存或异常，进入销售诊断。'),
        ('purchase_order_diagnosis', bool(ent['po_id']) and any(k in t for k in ['为什么','验收','到货','状态','剩余','诊断','收货']), 'purchase_diagnosis', '识别到采购订单号且问题涉及验收/状态，进入采购诊断。'),
        ('sku_query', bool(ent['sku']) and any(k in t for k in ['库存','采购','销售','流水','最近','多少','查询','变化']), 'sku_query', '识别到SKU且问题需要业务事实，进入SQL查询。'),
        ('stock_summary', any(k in t for k in ['库存汇总','安全库存','低库存','补货预警']), 'stock_summary', '问题要求库存汇总或安全库存判断，进入SQL汇总。'),
        ('sales_order_fallback', bool(ent['so_id']), 'sales_diagnosis', '仅识别到销售订单号，默认进入销售订单诊断。'),
        ('purchase_order_fallback', bool(ent['po_id']), 'purchase_diagnosis', '仅识别到采购订单号，默认进入采购订单诊断。'),
        ('sku_fallback', bool(ent['sku']), 'sku_query', '仅识别到SKU，默认进入SKU查询。'),
    ]:
        result=hit(*args)
        if result: return result[0],ent,result[1]
    checks.append({"rule":"knowledge_fallback","matched":True})
    return 'knowledge',ent,{"matched_rule":"knowledge_fallback","reason":"未识别结构化业务对象或测试意图，进入知识库检索。","checks":checks}

def route(text:str):
    kind,ent,_=route_with_reason(text)
    return kind,ent
