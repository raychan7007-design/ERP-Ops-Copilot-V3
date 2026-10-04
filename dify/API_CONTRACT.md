# Dify HTTP Tool API Contract

本地启动：`python -m app.web`。

## Health
`GET /api/health`

## Unified Query
`POST /api/query`

请求：
```json
{"query":"SO100为什么不能出库？"}
```

响应包含 `route`、`entities`、`answer/reason/action` 以及 `evidence`。Dify可以只负责Question Classifier和最终自然语言整合，把结构化事实交给这个只读工具。

安全设计：接口不接受任意SQL文本，内部只调用白名单参数化查询。
