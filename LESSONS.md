# Lessons

把踩过的坑写在这里，供以后的 Agent 阅读。只追加，不删旧条目。

## 2026-11-10 初始化仓库时

- 密钥只能放在 `.env`。主服务 `backend/app/config/settings.py` 里曾经把 DashScope API Key 写进默认值，教程目录 `backend/openai-agents-tutorial` 里也有多处写死的 `sk-` 密钥。这些不能进 Git；应改成环境变量或占位符。如果那些是真实可用的密钥，应在对应平台轮换。
- `.env`、`.venv`、`node_modules`、日志、Chroma 向量库（`chroma_kb1` 及其备份）、`user_memories`、爬取与临时数据都是本地数据，不要提交。
- 知识库前端目录名是 `front/knowlege_platform_ui`（少一个 d）。这是历史拼写，改名会牵动路径和文档，不要顺便「修正」。
- 主调度智能体当前使用 `sub_model`，不是注释里的 `main_model`。改模型前要先确认这是有意选择。
- 知识库侧已记下的待优化项（来自 `backend/knowledge/说明.txt`）：多路召回、排序模型、Markdown 中的图片（多模态）、去重、按动态阈值返回 Top N。做检索相关改动时优先考虑这些，不要另起一套互相冲突的方案。
