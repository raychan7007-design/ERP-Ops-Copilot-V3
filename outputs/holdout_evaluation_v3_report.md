# V3 封存 Holdout 评测

- 类型：sealed synthetic post-validation holdout; not production accuracy or independent third-party benchmark
- 数据集 SHA256：`6d06e4bbfbdf3e93d3ccdb8f9c10eab85c37b4e3f6e45b35587a8a470f01c245`
- Case：29/29 通过（100.0%）
- Router：29/29（100.0%）
- 结构/内容断言：42/42（100.0%）

> 这是开发验证完成后才执行的合成封存测试，不是生产准确率、真实用户效果或独立第三方评测。首次执行后不据此修改V3代码；失败项原样保留。

|ID|问题|期望路由|实际路由|结果|
|---|---|---|---|---|
|T01|PO100 还剩几台没验收？|purchase_diagnosis|purchase_diagnosis|PASS|
|T02|PO101 还有待收数量吗|purchase_diagnosis|purchase_diagnosis|PASS|
|T03|po102当前收货进度|purchase_diagnosis|purchase_diagnosis|PASS|
|T04|PO404|purchase_diagnosis|purchase_diagnosis|PASS|
|T05|SO100到底差多少库存？|sales_diagnosis|sales_diagnosis|PASS|
|T06|SO102出完后预计还剩多少？|sales_diagnosis|sales_diagnosis|PASS|
|T07|SO101查下来源流水|sales_diagnosis|sales_diagnosis|PASS|
|T08|SO404库存异常|sales_diagnosis|sales_diagnosis|PASS|
|T09|SKU001库存健康吗？|sku_query|sku_query|PASS|
|T10|SKU002最近变动记录|sku_query|sku_query|PASS|
|T11|SKU003安全库存是多少？|sku_query|sku_query|PASS|
|T12|目前有哪些低库存SKU？|stock_summary|stock_summary|PASS|
|T13|库存汇总里哪些是LOW？|stock_summary|stock_summary|PASS|
|T14|采购到货记录为什么不能脱离采购单？|knowledge|knowledge|PASS|
|T15|多次收货时什么时候从部分验收变成完成？|knowledge|knowledge|PASS|
|T16|收货数量比下单数量多应该怎么控制？|knowledge|knowledge|PASS|
|T17|只存当前库存数字有什么问题？|knowledge|knowledge|PASS|
|T18|库存变动日志要不要存变动前和变动后？|knowledge|knowledge|PASS|
|T19|出库前为什么要先检查可用库存？|knowledge|knowledge|PASS|
|T20|销售单从待出库到已经发货，状态怎么流转？|knowledge|knowledge|PASS|
|T21|库存更新失败以后为什么必须回滚？|knowledge|knowledge|PASS|
|T22|越权审批为什么必须拦截？|knowledge|knowledge|PASS|
|T23|用户验收阶段为什么还要测边界和异常？|knowledge|knowledge|PASS|
|T24|AS-IS和TO-BE在差异分析里怎么串起来？|knowledge|knowledge|PASS|
|T25|这个ERP模拟项目的真实性边界是什么？|knowledge|knowledge|PASS|
|T26|分批验收的验收用例怎么写？|uat|uat|PASS|
|T27|销售出库遇到库存不足，验收用例怎么写？|uat|uat|PASS|
|T28|角色权限的测试场景怎么覆盖？|uat|uat|PASS|
|T29|订单备注字段改为必填，测试场景怎么覆盖？|uat|uat|PASS|