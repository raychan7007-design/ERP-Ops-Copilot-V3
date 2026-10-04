# ERP Ops Copilot V3 状态

## 已完成

- ERP 演示数据库与 MySQL 兼容结构设计
- 白名单参数化只读 SQL Tools + Join/参数 Trace
- 采购/销售异常诊断 + 检查链 + 建议动作
- Router Trace
- 本地 RAG + Query Expansion + 来源证据
- UAT Assistant
- 本地 Web Demo + `/api/health` + `/api/query`
- Dockerfile / docker-compose / `.env.example`
- Dify OpenAPI、节点 Prompt、知识库材料、部署检查清单
- 架构图、Demo脚本、JD映射、面试追问树
- GitHub Pages 静态作品集页

## V3 实测

- 自动化测试：27/27 通过
- 固定合成功能回归：17/17
- RAG 合成检索：Recall@1=100%，Recall@3=100%，MRR=1.000
- 开发验证集：32/32 Case，48/48断言
- V3 封存 Holdout：29/29 Case，Router 29/29，42/42断言
- HTTP smoke：通过
- Python compileall：通过

所有数字均为本地、合成、作品集级回归，不是生产准确率或真实企业泛化能力。

## 可选增强，不影响当前投递

- 公网 HTTPS 后端
- Dify Cloud 真机工作流
- Docker 容器实机 build

当前不因免费部署平台要求绑卡而强行付费，也不虚构上线状态。
