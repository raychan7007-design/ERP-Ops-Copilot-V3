# 固定功能回归评测报告

- 类型：fixed synthetic functional regression; not model accuracy or production benchmark
- 案例：17
- 通过：17
- 失败：0
- 通过率：100%

> 注意：这是固定合成测试的功能回归，不是LLM准确率、生产质量或真实用户效果。

|问题|期望路由|实际路由|结果|
|---|---|---|---|
|PO100为什么还是部分验收？|purchase_diagnosis|purchase_diagnosis|PASS|
|PO102为什么还在待验收？|purchase_diagnosis|purchase_diagnosis|PASS|
|SO100为什么不能出库？|sales_diagnosis|sales_diagnosis|PASS|
|SO102现在能不能出库？|sales_diagnosis|sales_diagnosis|PASS|
|SKU001库存多少？|sku_query|sku_query|PASS|
|SKU003库存多少？|sku_query|sku_query|PASS|
|给我看库存汇总和安全库存|stock_summary|stock_summary|PASS|
|为什么库存余额还需要库存流水？|knowledge|knowledge|PASS|
|验收为什么必须关联采购订单？|knowledge|knowledge|PASS|
|Fit-Gap分析之后还要做什么？|knowledge|knowledge|PASS|
|销售库存不足怎么处理？|knowledge|knowledge|PASS|
|采购和销售角色为什么要分权限？|knowledge|knowledge|PASS|
|分批验收怎么做UAT？|uat|uat|PASS|
|库存不足出库怎么设计测试用例？|uat|uat|PASS|
|权限功能如何验收？|uat|uat|PASS|
|SO999为什么不能出库？|sales_diagnosis|sales_diagnosis|PASS|
|PO999状态是什么？|purchase_diagnosis|purchase_diagnosis|PASS|