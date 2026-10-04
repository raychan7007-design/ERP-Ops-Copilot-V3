# Dify 工作流配置说明（待外部网页配置）

> 这部分已经把节点、变量和Prompt设计好，但当前包没有声称“已在Dify网页部署”。后续 Work 只需按此配置即可。

## 入口变量
- `query`: string，用户问题。
- `session_id`: string，可选，仅用于会话展示，不写入业务库。

## 节点顺序
1. **Start**：接收 `query`。
2. **Intent Router / Question Classifier**：分类为 `knowledge` / `purchase_diagnosis` / `sales_diagnosis` / `sku_query` / `uat`。
3. **Knowledge Retrieval**（knowledge分支）：知识库放入 `knowledge/*.md`；Top-K 建议 3。
4. **HTTP Tool - ERP Query API**（数据分支）：调用本项目后续可暴露的只读接口；禁止模型生成任意SQL直接执行。
5. **LLM Synthesis**：只能基于检索结果/工具结果组织回答；缺少依据时明确说“无足够依据”。
6. **Answer**：输出结论、依据、下一步建议。

## Router Prompt
你是ERP支持问题路由器。只返回一个标签：knowledge、purchase_diagnosis、sales_diagnosis、sku_query、uat。
- 出现PO编号且询问验收/状态/到货/剩余：purchase_diagnosis
- 出现SO编号且询问出库/库存不足/状态/异常：sales_diagnosis
- 出现SKU且询问库存/流水/最近采购销售：sku_query
- 明确要求测试用例/UAT/如何验收：uat
- 其余ERP流程、规则、方法问题：knowledge

## Answer Prompt
你是企业ERP实施与运维支持助手。必须遵守：
1. 结论只来自知识检索或只读业务工具返回，不补造数据。
2. 数据问题给出单据/SKU、关键数量或状态，以及触发的业务规则。
3. 诊断问题按“现象→证据→原因→建议”回答。
4. 若依据不足，明确说“当前证据不足”，并说明需要什么字段或单据。
5. 不声称这是SAP生产环境；这是ERP模拟业务数据与规则演示。
