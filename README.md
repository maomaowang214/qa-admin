# QA Admin

前后端一体的 QA 管理后台：Web 前端 + FastAPI 后端，支持 Docker 一键部署。

## 项目结构

```
├─ backend               # 后端工程 (FastAPI + Python)
├─ frontend              # Web 前端工程
├─ devops                # 部署配置
├─ docker-compose.yaml   # Docker 编排文件
├─ deploy.sh             # 一键部署脚本
├─ LICENSE               # 开源协议
└─ README.md             # 本说明（中文）
```

## 快速开始

### 方式一：一键部署（推荐）

确保已安装 Docker 与 Docker Compose，并已配置 `backend/.env`（可从 `backend/.env.example` 复制）：

```bash
chmod +x deploy.sh
./deploy.sh
```

将启动后端服务、MySQL、Redis，并执行数据库迁移与种子数据。前端需本地单独启动（见下方「本地开发」）。

### 方式二：本地开发

**后端**

```bash
cd backend
cp .env.example .env   # 按需修改
pip install -r requirements.txt
# 创建数据库后执行迁移与种子
alembic upgrade head
python -m scripts.seed_data
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API 文档：<http://localhost:8000/docs>

**前端**

```bash
cd frontend
pnpm install
pnpm dev
```

前端已配置 Vite 代理：`/api` 会转发到后端 `http://localhost:8000`，确保后端先启动即可对接。

### 默认账号（种子数据）

| 用户名 | 密码     | 说明       |
| ------ | -------- | ---------- |
| admin  | admin123 | 超级管理员 |
| user   | user123  | 普通用户   |

## 技术栈

| 部分   | 技术说明                                  |
| ------ | ----------------------------------------- |
| 后端   | FastAPI、SQLAlchemy 2、PyJWT、APScheduler |
| 前端   | Vue、Vite、Vue Vben Admin                 |
| 数据库 | MySQL 8                                   |
| 缓存   | Redis（可选）                             |
| 部署   | Docker / Docker Compose                   |

## 更多说明

- 后端详细说明见 [backend/README.md](backend/README.md)
- 部署与 Nginx 示例见 [devops/README.md](devops/README.md)
