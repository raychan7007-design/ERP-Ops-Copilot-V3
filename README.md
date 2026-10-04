# ERP Ops Copilot｜企业 ERP 智能运维与实施支持 Agent

面向 **ERP 实施 / 企业信息化 / 系统管理** 求职作品集的可运行项目。核心不是“上传 PDF 然后聊天”的薄 RAG，而是把 **业务规则 + ERP 结构化数据 + 异常诊断 + UAT 辅助** 串成一条可解释工作流。

## 一句话架构

**用户问题 → Intent Router → RAG 知识检索 / SQL 只读 Tool / 规则诊断 / UAT 生成 → 证据化回答**

## 已实现

- SQLite ERP 演示库：商品、供应商、采购单/明细、销售单/明细、库存、库存流水
- 参数化只读 SQL Tools：库存、PO、SO、库存流水、库存汇总
- 采购诊断：待验收 / 部分验收 / 已完成、剩余验收量、来源流水
- 销售诊断：库存不足拦截、可出库判断、来源流水
- 离线 RAG：本地 TF-IDF/余弦检索知识库并返回来源
- UAT Assistant：正常、边界、异常、权限、一致性、幂等场景
- Router Trace、SQL Tool Trace、诊断检查链
- 本地 Web Demo：`/api/health`、`/api/query`
- Dockerfile / docker-compose / OpenAPI / Dify 工作流与 Prompt 设计
- 自动化测试、功能回归、RAG 回归、封存 Holdout

## 快速运行

要求 Python 3.10+，核心功能只使用标准库。

```bash
python scripts/build_db.py
python main.py "SO100为什么不能出库？"
python -m unittest discover -s tests -v
python -m app.web
```

浏览器打开 `http://127.0.0.1:8000`。

推荐 Demo：
- `PO100为什么还是部分验收？`
- `SO100为什么不能出库？`
- `SKU002现在库存多少？`
- `为什么库存余额还需要库存流水？`
- `新增分批验收功能怎么做UAT？`

## 为什么不是普通 RAG

1. 规则/流程问题 → RAG
2. 实时业务事实 → SQL Tool
3. 异常定位 → SQL 事实 + 业务规则
4. 需求验收 → UAT 生成

数据访问不允许模型执行任意 SQL，而是通过白名单、参数化只读函数完成。

## V3 实测

- 自动化测试：**27/27 通过**
- 固定合成功能回归：**17/17**
- RAG 合成检索：**Recall@1=100%，Recall@3=100%，MRR=1.000**
- 开发验证集：**32/32 Case，48/48 断言**
- 封存 V3 Holdout：**29/29 Case，Router 29/29，42/42 断言**
- 本地 HTTP smoke：通过
- Python compileall：通过

> 上述数字均为本地、合成、作品集级回归，不是生产准确率、真实企业泛化能力或第三方测评。

## 真实性边界

这是 **独立模拟作品集**：
- 不是真实客户项目
- 不是真实 SAP 配置、生产上线或企业运维记录
- SQLite 用于本地可复现演示
- 当前本地 RAG 不等价于生产级 Embedding/RAG
- GitHub Pages 只是作品集展示页，不冒充在线 Agent

## 在线与仓库状态

- GitHub Pages：`https://raychan7007-design.github.io/ERP-Ops-Copilot-V3/`
- 核心源码、测试、知识库、Dify 接入材料应直接展开在仓库根目录中，便于 HR 浏览
- Python 后端、SQL/RAG/诊断/UAT 链路已本地验证
- Dify Cloud 真机联调需要公网 HTTPS 后端；当前可用部署平台要求绑卡，因此不为“看起来上线”而付费或虚构上线状态
- `dify/` 中保留 OpenAPI、节点 Prompt、知识库清单和部署检查材料，后续有可用公网环境时可继续联调
