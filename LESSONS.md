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

## 2026-11-10 清理会让知识库失效的写法

- 没有在仓库里找到写死的可用密钥、反弹壳，或导入时向外发包的代码。对话页上的 `root1` / `123456` 是浏览器里的演示账号，接口不校验这组密码。不要把它当成后门删掉，也不要因此去拉黑名单。
- 知识库 `add_documents` 曾经把 `return` 写在 `for` 里面。默认一批 16 条，更长的文档只入库第一批，接口仍返回成功。这种「验证只看有没有返回」会把库写残。锁住的办法是：循环外面再返回，并用测试断言循环体里没有 `return`。
- 入库切分有两处会把文档切坏。一是长文档调用了 `split_documents(documents)`，同一批里的其它文档会被反复切开、短文档还会再留一份。二是分隔符列表里 `"\n**"` 和 `"\n\n"` 漏了逗号，相邻字符串被粘成一条，标题和空行都切不开。
- 上传接口把 `file.filename` 直接拼进临时目录。`/etc/passwd` 这种绝对路径在 `os.path.join` 里会丢掉前面的目录，`../` 会写到临时目录外面。文件名要先拒绝绝对路径和 `..`，再确认最终路径的父目录就是临时目录。`finally` 里使用的 `temp_file_path` 必须先设成 `None`，否则失败发生在赋值前会再抛 `UnboundLocalError`，把原来的错误盖住。
- 标题粗排对空标题 `continue` 之后，排序仍读取 `roughing_score`。爬取目录里只要有一个空标题的 Markdown，整次 `/query` 会 500。空标题要跳过，不能留在待排序列表里。某个标题文件打不开时，以前直接 `return []`，这一路已经找到的文档也丢掉。应该记下错误并继续看下一个文件。
- 长文档块的元数据键写成了 `chunk_index:`（多一个冒号）。重新打分时判断的是 `chunk_index`，条件永远不成立，事先算好的相似度用不上。这种键要写成同一个常量，不要各写各的字符串。
- 检索里有三处「文档来源」拼接，换行并不一致（入库带换行，长块检索和重排不带）。不要只改其中一处。向量库里已经嵌过的旧文本要一起重嵌，否则分数会对不上。这次没有改这三处字符串。
- `clean_markdown_images` 的正则对不上 `![描述](url)`，调用处也没有。不要把它当成已经可用的图片清洗。
- 知识库 `Settings` 的类体里如果写 `os.environ.get`，没配变量时缺省是 `None`，标成 `str` 会在导入时校验失败。缺省应是空字符串，环境变量和 `.env` 再覆盖。只在入口测试里补上变量，代码仍会在一台没有 `.env` 的机器上起不来。
- 主调度实际加载的是 `orchestrator_v1.md`。改 `orchestrator.md` 不会影响线上调度。不要删这份额外提示词，也不要只改它。
- 练习脚本不要命名成 `test_*.py`。`pytest` 会导入它们并执行顶层代码：`notes` 改名前的 `test_dir.py`、`test_jieba.py`、`test_beautifulsoup4.py` 都是这样。配置自检和日志自检同样不要放在 `test_` 开头的模块里，否则收集测试时就会去连数据库或读本机 `.env`。
- 知识库爬虫 `client.py` 捕获的是 `http.client.HTTPException`。`requests` 失败时抛的不是这个异常，这段 `except` 不会运行。修的时候要捕获 `requests` 自己的异常。
- `backend/app/infrastructure/tools/mcp/mcp_servers.py` 里手工试调用曾经写了 `search_mac_client` 和 `baidu_map_mcp`，文件里实际的变量不是这两个名字，直接运行会 `NameError`。试调用要引用同一个文件里创建的客户端。
- 生产环境的 CORS 仍是 `allow_origins=["*"]` 且 `allow_credentials=True`。这次不是在收紧跨域，所以没有改。不要顺手改掉。
- 已合并的对话页接口配置，不要再开一个内容相同的 PR 叠上去。空 diff 的 PR 应关掉，而不是继续往上提交第二套实现。
