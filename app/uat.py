from __future__ import annotations

def generate_uat(requirement:str):
    r=requirement.strip()
    cases=[]
    def add(cid,scenario,input_data,expected,kind,focus):
        cases.append({"id":cid,"kind":kind,"focus":focus,"scenario":scenario,"input":input_data,"expected":expected})
    req_type='generic'
    if any(k in r for k in ['分批验收','部分验收','累计验收']):
        req_type='partial_receipt'
        add('UAT-01','一次足量验收','采购5，验收5','累计验收=5，状态=验收完成，库存+5','normal','主流程')
        add('UAT-02','分两次完成验收','采购5，先验收3再验收2','第一次状态=部分验收；第二次状态=验收完成；累计=5','normal','状态流转')
        add('UAT-03','首次超量验收','采购5，首次验收6','拒绝提交；累计验收与库存不变','boundary','上限边界')
        add('UAT-04','部分验收后累计超量','采购5，已验收3，再验收3','拒绝第二次提交；累计仍=3；不产生异常库存流水','boundary','累计边界+一致性')
        add('UAT-05','零数量验收','采购5，验收0','拒绝提交并提示验收数量必须>0','invalid','下限边界')
        add('UAT-06','重复提交同一验收请求','采购5，已成功验收3，再重复提交相同请求','不得重复增加库存；需要幂等控制或人工确认','idempotency','重复提交')
    elif any(k in r for k in ['库存不足','超卖','销售出库']):
        req_type='sales_shipping'
        add('UAT-01','库存充足','库存10，销售5','允许进入待出库，预计出库后库存5','normal','主流程')
        add('UAT-02','库存恰好满足','库存5，销售5','允许出库，出库后库存0','boundary','库存边界')
        add('UAT-03','库存不足','库存3，销售5','阻止出库，不扣库存，不写成功流水','boundary','库存不足')
        add('UAT-04','销售数量为0','库存5，销售0','拒绝订单或出库操作','invalid','非法数量')
        add('UAT-05','持久化失败回滚','库存5，销售2，模拟写库失败','订单/库存/流水保持操作前一致','exception','事务一致性')
        add('UAT-06','重复出库请求','订单已出库后再次请求出库','不得重复扣减库存','idempotency','幂等')
    elif any(k in r for k in ['权限','角色','审批']):
        req_type='permission'
        add('UAT-01','授权角色操作','采购角色执行采购审批','审批成功并记录操作结果','normal','正向权限')
        add('UAT-02','越权操作','销售角色执行采购审批','拒绝并提示无权限','permission','越权')
        add('UAT-03','管理员操作','管理员执行审批','允许执行','normal','管理员')
        add('UAT-04','未登录/无角色','无有效身份执行审批','拒绝并记录安全事件','permission','缺失权限')
    else:
        add('UAT-01','正常主流程','满足前置条件','功能按需求完成','normal','主流程')
        add('UAT-02','边界值','输入等于业务阈值','按边界规则处理且状态正确','boundary','边界')
        add('UAT-03','非法输入','缺少必填或非法值','拒绝操作并返回明确提示','invalid','校验')
        add('UAT-04','重复提交','同一业务请求重复提交','避免重复数据或重复扣减','idempotency','幂等')
        add('UAT-05','异常回滚','关键写入阶段模拟异常','失败操作不留下部分状态','exception','一致性')
    dimensions=sorted(set(c['kind'] for c in cases))
    return {"requirement":r,"requirement_type":req_type,"coverage_dimensions":dimensions,
            "principles":["正常场景","边界场景","异常/权限场景","数据一致性/幂等"],"cases":cases,
            "generation_trace":{"method":"deterministic rule template","case_count":len(cases),"no_llm_required":True}}
