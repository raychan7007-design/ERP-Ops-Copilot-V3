# 架构说明

```text
用户问题
   │
   ▼
Intent Router ─────────────┐
 │                         │
 ├─ knowledge ──> Offline RAG / Dify Knowledge
 │                         │
 ├─ PO/SO diagnosis ──> Read-only SQL Tools ──> Rule Diagnosis
 │                         │
 ├─ SKU query ─────────> Read-only SQL Tools
 │                         │
 └─ UAT ───────────────> UAT Rule Generator
                           │
                           ▼
                 Evidence-first Response
```

设计重点：模型/Agent不直接执行任意SQL，只能调用参数化只读工具；诊断结论绑定订单、库存和规则证据；知识问题返回来源文档。
