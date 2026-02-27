# QA Admin 后台 API

基于 FastAPI 的后台管理系统后端，服务于 [Vue Vben Admin](https://github.com/vbenjs/vue-vben-admin) 前端（qa-admin）。

## 技术栈

| 项目     | 技术                    |
| -------- | ----------------------- |
| 后端框架 | FastAPI                 |
| ORM      | SQLAlchemy 2.0          |
| 定时任务 | APScheduler             |
| 认证     | PyJWT + Passlib         |
| 数据库   | MySQL (本机 13307)      |
| 缓存     | Redis（可选）           |
| 文档     | Swagger / Redoc         |
| 部署     | Docker / Docker Compose |

## 本地开发

### 1. 创建数据库

```bash
mysql -h127.0.0.1 -P13307 -uroot -proot -e "CREATE DATABASE IF NOT EXISTS qa_admin CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 环境变量

复制 `.env.example` 为 `.env`，按需修改（默认已适配本机 MySQL root/root:13307）。

### 4. 建表与种子数据

方式一（推荐，使用迁移）：

```bash
alembic upgrade head
python -m scripts.seed_data
```

方式二（仅跑种子，脚本内会 `init_db` 建表）：

```bash
python -m scripts.seed_data
```

### 5. 启动服务

**方式一（推荐）：自动打开 Swagger 文档**

```bash
python -m scripts.run_server
```

启动后会自动在浏览器打开 <http://localhost:8000/docs>。

**方式二：传统启动**

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Swagger 文档：<http://localhost:8000/docs>
- Redoc：<http://localhost:8000/redoc>

### 默认账号（种子数据）

| 用户名 | 密码     | 说明       |
| ------ | -------- | ---------- |
| admin  | admin123 | 超级管理员 |
| user   | user123  | 普通用户   |

## 接口说明（与前端约定）

- 统一响应：`{ "code": 0, "data": ... }`，`code !== 0` 为错误。
- 认证：请求头 `Authorization: Bearer <accessToken>`。
- 登录：`POST /auth/login`，请求体 `{ "username", "password" }`，返回 `{ "accessToken" }`。
- 刷新：`POST /auth/refresh`。
- 权限码：`GET /auth/codes`。
- 用户信息：`GET /user/info`。
- 侧栏菜单：`GET /menu/all`。
- 系统管理：`/system/role/*`、`/system/menu/*`、`/system/dept/*`（列表、增删改查及 name-exists、path-exists）。

前端 `apps/qa-admin` 的 `apiURL` 配置为 `http://localhost:8000` 即可对接本后端。

## Docker 部署

推荐在**项目根目录**使用统一编排（见根目录 `README.md` 与 `deploy.sh`）：

```bash
# 在 qa-admin 根目录
docker-compose up -d
```

若仅需在本目录启动后端 + MySQL + Redis，也可使用：

```bash
# 使用 compose 启动后端 + MySQL + Redis（在 backend 目录）
docker-compose up -d

# 首次需执行迁移与种子
docker-compose exec backend alembic upgrade head
docker-compose exec backend python -m scripts.seed_data
```

## 项目结构（便于扩展）

```
qa-py/
├── app/
│   ├── api/v1/          # 接口：auth, user, menu, system(role/menu/dept)
│   ├── core/            # 安全、依赖注入
│   ├── models/          # SQLAlchemy 模型
│   ├── schemas/         # Pydantic 模型
│   ├── tasks/           # APScheduler 定时任务
│   ├── config.py
│   ├── database.py
│   └── main.py
├── alembic/             # 数据库迁移
├── scripts/
│   └── seed_data.py     # 模拟数据
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── .env.example
```

扩展新模块时：在 `app/models` 增加模型，`app/schemas` 增加 Schema，`app/api/v1` 增加路由并挂到 `router.py`。
