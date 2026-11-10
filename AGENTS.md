# ITS 多智能体项目（给 Agent 用）

这是一套智能客服系统：用户在前端提问，主调度智能体把任务交给「资讯与技术专家」或「全能业务智能体」（服务站查询与地图导航），并接知识库、搜索 MCP、百度地图 MCP。

改代码前先读本文件和 `LESSONS.md`。密钥、日志、向量库、用户记忆都不要提交到 Git。

## 目录

- `backend/app`：主 API（FastAPI，本地 `127.0.0.1:8000`），多智能体与会话记忆。
- `backend/knowledge`：知识库服务（上传、检索、RAG，本地 `127.0.0.1:8001`）。
- `front/agent_web_ui`：对话前端（Vue + Vite，包名 `its-vue`）。
- `front/knowlege_platform_ui`：知识库管理前端。目录名拼写是 `knowlege`，不要擅自改名，以免路径和文档对不上。
- `backend/openai-agents-tutorial`：课程教程示例，不是线上服务；不要把它的改动当成产品修复。

## 智能体怎么分工

- 主调度：`backend/app/multi_agent/orchestrator_agent.py`，提示词来自 `backend/app/prompts/orchestrator_v1.md`。当前使用 `sub_model`。
- 资讯与技术专家：故障、操作说明、实时资讯；工具是本地知识库查询和搜索 MCP。
- 全能业务智能体：附近维修点、线下门店、路径规划；工具是本地服务站查询和百度地图 MCP。
- 调度通过 `backend/app/multi_agent/agent_factory.py` 里的两个 tool 转交，不要改写用户原话再往下传。

主对话接口是 `POST /api/query`（SSE）。会话列表是 `POST /api/user_sessions`。知识库上传是知识库服务的 `POST /upload`，检索问答是 `POST /query`。

## 配置与秘密

- 密钥只放在各服务自己的 `.env`：`backend/app/.env`、`backend/knowledge/.env`。可先复制对应的 `.env.example`。
- 主服务至少要配好「硅基流动」或「阿里百炼」其中一套，否则启动会失败。
- 不要把 API Key、token、密码写进源代码、默认值、测试或教程示例。如果发现写死的密钥，改成从环境变量读取，不要把原值写进 commit、PR 或评论。
- 不要提交：`.env`、`.venv`、`node_modules`、`logs/`、`backend/app/user_memories/`、`backend/knowledge/chroma_kb1*`、爬取与临时数据目录。

## 怎么本地跑

主服务在 `backend/app` 下安装依赖并启动 `api/main.py`（8000 端口）。知识库服务在 `backend/knowledge` 下启动 `api/main.py`（8001 端口）。前端分别在对应目录执行 `npm install` 和 `npm run dev`。改完后要真正跑起来验证，不要只看代码。

## 改代码规则

- 默认开 PR，不要直接推破坏性改动到 `main`。PR 要说清楚用户能感知到的行为变化。
- 先写或补测试，再改行为；已有测试失败必须修，或单独提 issue 说明原因。
- 不要为了「看起来干净」去重命名 `knowlege_platform_ui`，或删除 `LESSONS.md` 里的旧条目。
- 生产环境不要长期保持 CORS `allow_origins=["*"]`；若这次任务不是在收紧跨域，不要顺手改它。
- 知识库入库与检索改动要保证切片语义完整、元数据能辅助检索；相关待办见 `LESSONS.md`。

## 什么情况开 PR

- 能复现的 bug、明确的功能需求、测试或 CI 失败，并且已经有完整修复。
- 修复里不得包含密钥、用户记忆、日志或向量库数据。

## 什么情况只评论，或什么都不做

- 信息不足、无法复现、与本项目无关、重复 issue：只评论需要哪些信息，或标明重复项。
- 只涉及教程示例、不影响 `backend/app` 与 `backend/knowledge` 主流程：优先只评论；非改不可时把范围写清楚。
- 改动会把密钥或用户数据带进仓库：只评论指出风险，不要提交这些内容。
- 没有把握的大重构、与当前任务无关的风格清理：什么都不做。

## 输出长什么样

- Commit / PR 标题用简短中文或英文，说清改了什么行为，例如：`修复知识库上传后检索不到新文档`。
- PR 正文写：改了什么、怎么验证、有没有残留风险。不要粘贴 `.env`、密钥或完整用户会话。
- 若这次踩到新坑，把教训追加到 `LESSONS.md` 末尾，不要改写或删除旧条目。
