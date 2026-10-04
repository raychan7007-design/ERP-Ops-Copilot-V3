# Dify 部署后验收 Case

> 这些 Case 用于 Dify 真机部署后的人工验收，不计入本地 V3 holdout 指标。

| # | 问题 | 期望分支 | 核心核验点 |
|---:|---|---|---|
| 1 | PO100为什么还是部分验收？ | purchase_diagnosis | 采购5、已收3、剩余2 |
| 2 | PO102到货了吗？ | purchase_diagnosis | 累计验收0、待验收 |
| 3 | SO100为什么不能出库？ | sales_diagnosis | 需求5、库存3、BLOCK |
| 4 | SO102现在能出库吗？ | sales_diagnosis | 库存满足、ALLOW |
| 5 | SKU002现在库存多少？ | sku_query | 当前库存16、附最近流水 |
| 6 | 哪些SKU低于安全库存？ | stock_summary | 能看到 LOW 状态 |
| 7 | 为什么库存余额还要保留库存流水？ | knowledge | 命中库存追溯知识 |
| 8 | 超量验收为什么必须拦截？ | knowledge | 命中采购验收规则 |
| 9 | 分批验收需求如何做UAT？ | uat | 正常/边界/异常/幂等 |
| 10 | 销售角色做采购审批怎么验收？ | uat | 权限正反场景 |
| 11 | SO999为什么不能出库？ | sales_diagnosis | 明确“未找到业务对象” |
| 12 | 你们真实上线过SAP吗？ | knowledge | 不得声称真实SAP上线 |
