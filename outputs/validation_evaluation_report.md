# V3 开发验证集评测

- 类型：synthetic validation/acceptance set; used during V3 development; not holdout or production accuracy
- 数据集 SHA256：`09983b338fb09fd8ee32c7137c5752f720127e89dbf332d02484e661b6beed67`
- Case：32/32 通过（100.0%）
- Router：32/32（100.0%）
- 结构/内容断言：48/48（100.0%）

> 这是V3工程化后执行的合成验证集，不是生产准确率、真实用户效果或独立第三方评测。首次执行后不据此修改V3代码；失败项原样保留。

|ID|问题|期望路由|实际路由|结果|
|---|---|---|---|---|
|H01|帮我看下 PO-100 还差多少没收货|purchase_diagnosis|purchase_diagnosis|PASS|
|H02|采购单po101是不是已经验完了|purchase_diagnosis|purchase_diagnosis|PASS|
|H03|PO102 到货了吗？|purchase_diagnosis|purchase_diagnosis|PASS|
|H04|PO999 查一下现在什么状态|purchase_diagnosis|purchase_diagnosis|PASS|
|H05|SO-100 卡在哪里，怎么处理？|sales_diagnosis|sales_diagnosis|PASS|
|H06|SO102 这单现在可以发货吗|sales_diagnosis|sales_diagnosis|PASS|
|H07|so101 已经出库了吗？|sales_diagnosis|sales_diagnosis|PASS|
|H08|SO999 帮我定位一下异常|sales_diagnosis|sales_diagnosis|PASS|
|H09|SKU2 现在有几件？|sku_query|sku_query|PASS|
|H10|sku1 最近的库存流水给我看看|sku_query|sku_query|PASS|
|H11|SKU3 还有没有货？|sku_query|sku_query|PASS|
|H12|SKU999 库存情况|sku_query|sku_query|PASS|
|H13|哪些商品已经低于安全库存？|stock_summary|stock_summary|PASS|
|H14|给我看一下全部库存汇总|stock_summary|stock_summary|PASS|
|H15|收货为什么一定要关联采购订单？|knowledge|knowledge|PASS|
|H16|库存台账到底是干嘛的？|knowledge|knowledge|PASS|
|H17|ERP里怎么防止超卖？|knowledge|knowledge|PASS|
|H18|Fit Gap做完差异识别之后下一步是什么？|knowledge|knowledge|PASS|
|H19|用户验收测试一般应该覆盖哪些情况？|knowledge|knowledge|PASS|
|H20|为什么采购和销售角色要做权限隔离？|knowledge|knowledge|PASS|
|H21|采购单只到了一部分货，后面再到货怎么处理？|knowledge|knowledge|PASS|
|H22|库存不够时销售订单为什么不能先出库？|knowledge|knowledge|PASS|
|H23|新增分批验收需求，如何验收？|uat|uat|PASS|
|H24|库存不足时禁止销售出库，这个需求的测试场景有哪些？|uat|uat|PASS|
|H25|采购审批权限怎么做UAT？|uat|uat|PASS|
|H26|新增一个必填字段，测试用例怎么设计？|uat|uat|PASS|
|H27|重复提交销售出库请求的测试用例|uat|uat|PASS|
|H28|SKU 002 最近采购销售怎么变化？|sku_query|sku_query|PASS|
|H29|低库存补货预警现在怎么判断？|stock_summary|stock_summary|PASS|
|H30|采购5件已经收3件，还能再收3件吗？|knowledge|knowledge|PASS|
|H31|销售订单扣库存时写库失败，订单状态应该怎么办？|knowledge|knowledge|PASS|
|H32|这个作品可以说自己做过真实SAP上线吗？|knowledge|knowledge|PASS|