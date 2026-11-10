# Lessons

把踩过的坑写在这里，供以后的 Agent 阅读。只追加，不删旧条目。

## 2026-11-10 初始化仓库时

- 密钥只能放在 `.env`。主服务 `backend/app/config/settings.py` 里曾经把 DashScope API Key 写进默认值，教程目录 `backend/openai-agents-tutorial` 里也有多处写死的 `sk-` 密钥。这些不能进 Git；应改成环境变量或占位符。如果那些是真实可用的密钥，应在对应平台轮换。
- `.env`、`.venv`、`node_modules`、日志、Chroma 向量库（`chroma_kb1` 及其备份）、`user_memories`、爬取与临时数据都是本地数据，不要提交。
- 知识库前端目录名是 `front/knowlege_platform_ui`（少一个 d）。这是历史拼写，改名会牵动路径和文档，不要顺便「修正」。
- 主调度智能体当前使用 `sub_model`，不是注释里的 `main_model`。改模型前要先确认这是有意选择。
- 知识库侧已记下的待优化项（来自 `backend/knowledge/说明.txt`）：多路召回、排序模型、Markdown 中的图片（多模态）、去重、按动态阈值返回 Top N。做检索相关改动时优先考虑这些，不要另起一套互相冲突的方案。

## 2026-11-10 补 README 时

- `backend/app/seed_repair_shops.py` 曾经把数据库连接写死，库名也和 `.env.example` 的 `MYSQL_DATABASE`（`its_db`）不一致。样例数据脚本要读 `MYSQL_*`，不要再写死连接信息，文档里也不要出现那组连接值。
- 主服务 `requirements.txt` 当时没有 `pydantic` / `pydantic-settings`，只按文件安装无法加载 `config.settings`。知识库启动会导入上传路由和文档切分，原先缺 `aiofiles` 和 `langchain-text-splitters`。
- 主调度当前用 `sub_model`，客户端指向阿里百炼。只配硅基流动时进程能通过启动校验，对话请求仍会走到百炼那一侧。README 要把这件事写清楚。

## 2026-11-10 核对主服务能否按 README 启动

- `backend/app/infrastructure/ai/openai_client.py` 会在导入时同时构造硅基流动和阿里百炼两个客户端。`AsyncOpenAI` 在 `api_key` 为空时直接抛错，主进程还没监听端口就退出。这和 settings 里「至少一套即可」不一致。缺 key 或 base url 的那一侧要用本机占位客户端，不要在导入阶段去连真实地址。
- 只执行 `Settings()` 不能证明 `python api/main.py` 能起来。导入链会经过 `openai_client`。
- 在 `backend/app` 或 `backend/knowledge` 里执行 `python api/main.py` 时，解释器把 `sys.path[0]` 设成 `api/` 目录，`import api` 会失败。入口脚本要把服务根目录放回 `sys.path`。用 `python -c "import api.main"` 看不出来。
- `runpy.run_path('api/main.py')` 不会把脚本目录放进 `sys.path`，而 `python -c` 仍把当前目录留在搜索路径里。这样写的入口测试，删掉入口里的路径修复也会通过。要锁住 `python api/main.py`，得先把 `api/` 放到 `sys.path[0]`，并拿掉 `''` 和服务根目录。
- 知识库 `Settings.KNOWLEDGE_BASE_URL` 标成 `str`，类体里的默认值是 `os.environ.get`，没配又没有 `.env` 时就是 `None`，导入阶段直接校验失败。`.env.example` 里这一行是空字符串，空字符串可以启动上传和问答。入口测试要自己写上这个变量，不能靠本机 `.env` 把失败藏起来。

## 2026-11-10 补 Windows 虚拟环境命令时

- README 里只写 `source .venv/bin/activate` 时，Windows 命令提示符要用 `.venv\Scripts\activate`，PowerShell 要用 `.venv\Scripts\Activate.ps1`。不要只留 Unix 那一条。

## 2026-11-10 对话页不要写死 127.0.0.1

- `front/agent_web_ui` 的接口地址不要写死成 `http://127.0.0.1:8000`。留空 `VITE_API_BASE_URL` 时走 Vite 的 `/api` 代理，目标由 `VITE_DEV_PROXY_TARGET` 决定，默认仍是本机 8000。浏览器要直连别的机器时才填 `VITE_API_BASE_URL`。

## 2026-11-10 开发代理地址不要用 VITE_ 前缀

- Vite 会把以 `VITE_` 开头的变量写进浏览器能读到的 `import.meta.env`。对话页代理目标如果叫 `VITE_DEV_PROXY_TARGET`，`npm run dev` 打开页面就能看到这个地址。只给 `vite.config.js` 用的目标应叫 `API_PROXY_TARGET`，用 `loadEnv` 读取，不要加 `VITE_` 前缀。浏览器直连才用 `VITE_API_BASE_URL`。
