# RAG检索回归评测

- 类型：hand-authored synthetic retrieval regression; not production RAG accuracy
- 案例：13
- Recall@1：100.0%
- Recall@3：100.0%
- MRR：1.000

> 注意：这是本项目知识库上的合成检索回归，用于验证常见改写能否命中预期章节，不代表生产RAG效果。

|问题|期望Chunk|排名|Top3|
|---|---|---:|---|
|验收为什么必须挂在采购单下面？|01_procurement_receiving:1|1|01_procurement_receiving:1, 01_procurement_receiving:2, 01_procurement_receiving:intro|
|采购5个先收3个，订单是什么状态？|01_procurement_receiving:2|1|01_procurement_receiving:2, 01_procurement_receiving:1, 01_procurement_receiving:3|
|到货数量超过采购数量怎么办？|01_procurement_receiving:3|1|01_procurement_receiving:3, 01_procurement_receiving:1, 01_procurement_receiving:2|
|库存余额和库存台账有什么区别？|02_inventory_traceability:1|1|02_inventory_traceability:1, 01_procurement_receiving:3, 02_inventory_traceability:2|
|库存流水里至少要记录哪些字段？|02_inventory_traceability:2|1|02_inventory_traceability:2, 02_inventory_traceability:1, 03_sales_shipping:3|
|什么时候需要补货预警？|02_inventory_traceability:3|1|02_inventory_traceability:3, 02_inventory_traceability:1, 03_sales_shipping:2|
|为什么不能库存不够也先发货？|03_sales_shipping:1|1|03_sales_shipping:1, 02_inventory_traceability:1, 03_sales_shipping:2|
|销售单库存不足时状态怎么处理？|03_sales_shipping:2|1|03_sales_shipping:2, 03_sales_shipping:1, 02_inventory_traceability:1|
|写库存失败以后订单已经更新怎么办？|03_sales_shipping:3|1|03_sales_shipping:3, 03_sales_shipping:1, 01_procurement_receiving:1|
|销售角色能不能做采购审批？|04_permissions_uat:1|1|04_permissions_uat:1, 04_permissions_uat:intro, 01_procurement_receiving:1|
|用户验收测试需要覆盖哪些情况？|04_permissions_uat:2|1|04_permissions_uat:2, 04_permissions_uat:intro, 01_procurement_receiving:2|
|Fit-Gap分析不能只写缺功能还要做什么？|05_fit_gap_method:1|1|05_fit_gap_method:1, 05_fit_gap_method:intro, 04_permissions_uat:2|
|这个项目能不能说自己做过SAP上线？|05_fit_gap_method:2|1|05_fit_gap_method:2, 05_fit_gap_method:1, 03_sales_shipping:1|