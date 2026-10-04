# RAG 质量与边界

当前本地版本不下载 Embedding 模型，采用可解释的轻量检索：

1. 中文字符 unigram/bigram + 英文/数字 token；
2. TF-IDF-like 权重；
3. 余弦相似度；
4. ERP 领域少量 query expansion，例如“收货→验收/到货/入库”“库存台账→库存流水/追溯”；
5. 返回 Top-K、分数、命中词与来源章节；相关性过低时拒绝直接给结论。

`outputs/rag_evaluation_report.md` 是手工编写的**合成检索回归**，目的是验证常见问法能否命中预期章节。它不是生产准确率，也没有独立真实用户测试集。

后续在 Dify 中部署时，可以把当前 Markdown 知识库上传后切换到真正的向量 Embedding + rerank，但必须重新做检索评测，不能沿用本地分数。
