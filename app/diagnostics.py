from __future__ import annotations
from .sql_tools import get_purchase_order,get_sales_order,get_stock,movements_by_source,explain_tool

def diagnose_purchase(po_id,db_path=None):
    kw={} if db_path is None else {'db_path':db_path}
    po=get_purchase_order(po_id,**kw)
    movements=movements_by_source(po_id,**kw)
    checks=[
        {"check":"received_not_negative","actual":po['received_qty'],"expected":">=0","pass":po['received_qty']>=0},
        {"check":"received_not_over_ordered","actual":po['received_qty'],"expected":f"<= {po['ordered_qty']}","pass":po['received_qty']<=po['ordered_qty']},
        {"check":"remaining_consistent","actual":po['remaining_qty'],"expected":po['ordered_qty']-po['received_qty'],"pass":po['remaining_qty']==po['ordered_qty']-po['received_qty']},
    ]
    if po['status']=='PARTIAL_RECEIVED':
        reason=f"采购{po['ordered_qty']}件，累计验收{po['received_qty']}件，剩余{po['remaining_qty']}件未验收，因此状态为部分验收。"
        action="继续按原采购单登记剩余到货；每次验收数量必须大于0且不得超过剩余待验收量。"
        checks.append({"check":"partial_status_rule","actual":po['received_qty'],"expected":f"0 < received_qty < {po['ordered_qty']}","pass":0<po['received_qty']<po['ordered_qty']})
    elif po['status']=='PENDING_RECEIPT':
        reason=f"采购{po['ordered_qty']}件，当前累计验收0件，因此仍处于待验收。"
        action="收到货后引用该PO登记验收；首次验收不得超过采购数量。"
        checks.append({"check":"pending_status_rule","actual":po['received_qty'],"expected":0,"pass":po['received_qty']==0})
    elif po['status']=='RECEIVED':
        reason=f"累计验收{po['received_qty']}件已达到采购数量{po['ordered_qty']}件，订单已完成验收。"
        action="如需核对库存变化，可查看该PO对应库存流水。"
        checks.append({"check":"received_status_rule","actual":po['received_qty'],"expected":po['ordered_qty'],"pass":po['received_qty']==po['ordered_qty']})
    else:
        reason=f"当前订单状态为{po['status']}。"; action="按订单状态和业务规则进一步核对。"
    return {"type":"purchase_diagnosis","record":po,"reason":reason,"action":action,"checks":checks,
            "evidence":{"source":"SQL","movements":movements},
            "tool_trace":[explain_tool('get_purchase_order',{'po_id':po_id.upper()}),explain_tool('movements_by_source',{'source_id':po_id.upper()})]}

def diagnose_sales(so_id,db_path=None):
    kw={} if db_path is None else {'db_path':db_path}
    so=get_sales_order(so_id,**kw); stock=get_stock(so['sku'],**kw); movements=movements_by_source(so_id,**kw)
    checks=[
        {"check":"qty_positive","actual":so['qty'],"expected":">0","pass":so['qty']>0},
        {"check":"stock_non_negative","actual":stock['stock_qty'],"expected":">=0","pass":stock['stock_qty']>=0},
        {"check":"stock_sufficient","actual":stock['stock_qty'],"expected":f">= {so['qty']}","pass":stock['stock_qty']>=so['qty']},
    ]
    if so['status']=='BLOCKED_STOCK' or so['qty']>stock['stock_qty']:
        shortage=max(0,so['qty']-stock['stock_qty'])
        reason=f"订单需求{so['qty']}件，当前可用库存{stock['stock_qty']}件，需求超过库存，命中库存不足校验，因此阻止出库。"
        action=f"补货至少{shortage}件后重新校验，或按业务规则调整订单数量。"
        decision={"result":"BLOCK","shortage_qty":shortage}
    elif so['status']=='READY_TO_SHIP':
        reason=f"订单需求{so['qty']}件，当前库存{stock['stock_qty']}件，库存满足，订单已进入待出库。"
        action="由仓储角色执行出库，出库成功后写库存流水并更新状态。"
        decision={"result":"ALLOW","projected_stock_after":stock['stock_qty']-so['qty']}
    elif so['status']=='SHIPPED':
        reason="订单已完成出库。"; action="如需核对可查看该SO来源流水。"; decision={"result":"COMPLETED"}
    else:
        reason=f"当前订单状态为{so['status']}。"; action="按状态规则继续处理。"; decision={"result":"REVIEW"}
    return {"type":"sales_diagnosis","record":so,"stock":stock,"reason":reason,"action":action,"decision":decision,"checks":checks,
            "evidence":{"source":"SQL","movements":movements},
            "tool_trace":[explain_tool('get_sales_order',{'so_id':so_id.upper()}),explain_tool('get_stock',{'sku':so['sku']}),explain_tool('movements_by_source',{'source_id':so_id.upper()})]}
