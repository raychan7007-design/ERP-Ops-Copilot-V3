# Dify 最小部署检查清单

## 在进入 Work / Dify 前已经准备好

- [x] 本地 HTTP API：`GET /api/health`、`POST /api/query`
- [x] OpenAPI 定义：`dify/openapi.yaml`
- [x] 知识库材料：`knowledge/*.md`
- [x] Router 与 Answer Prompt：`dify/NODE_PROMPTS.md`
- [x] 本地功能、RAG、Holdout 评测脚本
- [x] Docker 运行文件

## 需要外部环境时才做

1. 将本项目部署到可从公网访问的 HTTPS 地址。
2. 把 `dify/openapi.yaml` 中的 server URL 替换为实际地址。
3. 在 Dify 导入 HTTP Tool / OpenAPI。
4. 新建知识库并上传 `knowledge/*.md`。
5. 建立 Router：knowledge / purchase_diagnosis / sales_diagnosis / sku_query / stock_summary / uat。
6. knowledge 分支使用 Knowledge Retrieval；其余分支调用 `/api/query`。
7. 最终 LLM 只做事实整合，不允许补造 Tool 未返回信息。
8. 用 `docs/dify_acceptance_cases.md` 跑验收并截图。

## 需要用户本人介入

- 登录 / 2FA / CAPTCHA
- 创建或填入自己的模型 API Key
- 任何付费或云资源确认
