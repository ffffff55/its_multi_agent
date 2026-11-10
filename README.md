# ITS 多智能体客服

用户在对话页提问后，主调度智能体把任务交给两个专家之一：

- **资讯与技术专家**：故障、操作说明、实时资讯。用本地知识库和联网搜索。
- **全能业务智能体**：附近维修点、线下门店、路径规划。用本地服务站数据和百度地图。

调度不会改写用户原话，只把原问题转交。

`backend/openai-agents-tutorial` 是课程示例，不是这套服务。要跑产品，按下面的主服务、知识库和两个前端来。

## 目录

| 路径 | 作用 | 本地地址 |
| --- | --- | --- |
| `backend/app` | 主 API（对话、会话） | `http://127.0.0.1:8000` |
| `backend/knowledge` | 知识库（上传、检索、回答） | `http://127.0.0.1:8001` |
| `front/agent_web_ui` | 对话前端，包名 `its-vue` | Vite 默认 `http://127.0.0.1:5173` |
| `front/knowlege_platform_ui` | 知识库管理前端。目录名是 `knowlege`，少一个 d | `http://127.0.0.1:3000` |

## 准备

- Python 3 和 Node.js
- 至少一套大模型账号。硅基流动（`SF_API_KEY` + `SF_BASE_URL`）或阿里百炼（`AL_BAILIAN_API_KEY` + `AL_BAILIAN_BASE_URL`）必须有一套，否则主服务在启动校验时退出。只配其中一套时，进程可以起来。
- 当前主调度用的是子模型，客户端指向阿里百炼。只配了硅基流动时，对话请求会失败。要真正对话，请配好 `AL_BAILIAN_API_KEY`、`AL_BAILIAN_BASE_URL` 和 `SUB_MODEL_NAME`。
- 查附近服务站需要 MySQL。只问故障和操作说明时可以先不装。
- 联网搜索需要通义千问 DashScope；地图和路径需要百度地图 AK。这两项缺失时进程仍会启动，对应工具会失败。

密钥只放在各自的 `.env` 里。不要把填好的 `.env`、日志、`backend/app/user_memories/`、`backend/knowledge/chroma_kb1*` 提交到 Git。

## 1. 知识库服务

```bash
cd backend/knowledge
python -m venv .venv
```

激活虚拟环境。macOS 和 Linux：

```bash
source .venv/bin/activate
```

Windows 命令提示符：

```bat
.venv\Scripts\activate
```

Windows PowerShell：

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 提示无法运行脚本，用上面的命令提示符命令。激活后再安装依赖并复制配置：

```bash
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`，至少填写：

- `API_KEY`、`BASE_URL`：对话模型和向量模型的接口
- `MODEL`：回答用的模型名
- `EMBEDDING_MODEL`：入库和检索用的向量模型名

然后启动（工作目录必须是 `backend/knowledge`）：

```bash
python api/main.py
```

服务听 `127.0.0.1:8001`。上传和检索都会在本机目录 `chroma_kb1` 里建向量库，这个目录不要提交。

上传一篇 Markdown：

```bash
curl -F "file=@你的文档.md" http://127.0.0.1:8001/upload
```

直接问知识库：

```bash
curl -X POST http://127.0.0.1:8001/query \
  -H 'Content-Type: application/json' \
  -d '{"question":"笔记本开不了机怎么办"}'
```

## 2. 主服务

```bash
cd backend/app
python -m venv .venv
```

激活方式和知识库一样。macOS 和 Linux 用 `source .venv/bin/activate`，Windows 命令提示符用 `.venv\Scripts\activate`，PowerShell 用 `.venv\Scripts\Activate.ps1`。然后：

```bash
pip install -r requirements.txt
cp .env.example .env
```

编辑 `.env`。变量名和含义以 `.env.example` 为准，常见一组本地值是：

- `KNOWLEDGE_BASE_URL=http://127.0.0.1:8001`
- `SUB_MODEL_NAME` 填百炼上实际可用的模型名
- 需要服务站时填写 `MYSQL_HOST`、`MYSQL_PORT`、`MYSQL_USER`、`MYSQL_PASSWORD`、`MYSQL_DATABASE`（示例里的库名是 `its_db`）
- 需要搜索或地图时再填 `DASHSCOPE_BASE_URL`、`DASHSCOPE_API_KEY`、`BAIDUMAP_AK`

先建库（库名要和 `MYSQL_DATABASE` 一致），再写入样例服务站。样例脚本读的是同一份 `MYSQL_*`，表里已有数据时不会重复插入。

```bash
mysql -e "CREATE DATABASE IF NOT EXISTS its_db CHARACTER SET utf8mb4;"
python seed_repair_shops.py
```

启动（工作目录必须是 `backend/app`）：

```bash
python api/main.py
```

服务听 `127.0.0.1:8000`。启动时会尝试连接搜索和百度地图；连不上只记错误日志，进程继续跑。

发起一轮对话（SSE，响应类型是 `text/event-stream`）：

```bash
curl -N -X POST http://127.0.0.1:8000/api/query \
  -H 'Content-Type: application/json' \
  -d '{"query":"笔记本开不了机怎么办","context":{"user_id":"demo-user"},"flag":true}'
```

拉取该用户的会话列表：

```bash
curl -X POST http://127.0.0.1:8000/api/user_sessions \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"demo-user"}'
```

## 3. 前端

对话页请求已经写死到 `http://127.0.0.1:8000`，先启动主服务。

```bash
cd front/agent_web_ui
npm install
npm run dev
```

知识库管理页把 `/api` 代理到 `http://127.0.0.1:8001`，先启动知识库服务。

```bash
cd front/knowlege_platform_ui
npm install
npm run dev
```

## 调用时怎么分工

- 故障、操作说明、产品资讯：走资讯与技术专家，会查知识库，配置了搜索时还会联网。
- 附近维修点、门店、怎么去：走全能业务智能体，会查 MySQL 里的服务站，配置了百度地图时还会做定位和路径。
