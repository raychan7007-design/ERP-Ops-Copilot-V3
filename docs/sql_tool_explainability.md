# SQL Tool 可解释性设计

本项目不允许 Agent 直接生成任意 SQL 后执行。数据访问只通过白名单参数化 Tool 完成，降低误查询和写库风险，同时方便面试时解释“查了什么、为什么查”。

## Tool 目录

- `get_stock(sku)`：`products JOIN inventory`，查询当前库存与安全库存。
- `get_purchase_order(po_id)`：`purchase_orders JOIN suppliers JOIN purchase_order_items JOIN products`，查询采购量、累计验收量、剩余量。
- `get_sales_order(so_id)`：`sales_orders JOIN sales_order_items JOIN products JOIN inventory`，查询订单量与当前库存。
- `recent_movements(sku)`：按SKU查询最近库存流水。
- `movements_by_source(source_id)`：按PO/SO追溯来源流水。
- `stock_summary()`：汇总所有SKU库存健康状态。

## 为什么不用 Text-to-SQL

作品集目标是展示 ERP 运维诊断和多表查询能力，而不是展示一个不可控的自由 SQL Agent。白名单 Tool 有三个好处：

1. **安全**：只有 SELECT，没有 INSERT/UPDATE/DELETE；
2. **可解释**：每个 Tool 都能返回用途、涉及表、Join 关系和参数；
3. **可测试**：同一问题会稳定落到固定查询，方便回归验证。

如果未来接入真实企业环境，可以在数据库只读账号、查询超时、行数限制、审计日志基础上，再评估受控 Text-to-SQL。
