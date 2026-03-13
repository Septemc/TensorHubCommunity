# TensorHubCommunity

TensorHub 社区 MVP，包含：

- `backend/`：FastAPI + SQLAlchemy async + PostgreSQL
- `frontend/`：Vue 3 + TypeScript + Vite + Pinia + Element Plus
- `deploy/`：Nginx 配置

## 启动方式

1. Docker 方式：复制根目录 `.env.example` 为 `.env`，执行 `docker compose up -d db backend`。
2. 本地后端方式：复制 `backend/.env.example` 为 `backend/.env`，确保本机 PostgreSQL 监听 `5432`，再执行 `uvicorn app.main:app --reload`。
3. 前端执行 `npm install` 后运行 `npm run dev`。
4. 首次启动会自动创建默认角色、基础页面和管理员账号。

## 默认能力

- 实名注册、登录、Cookie 鉴权、管理员审核
- 官网首页、团队介绍、公告管理
- 论坛板块、帖子、评论、点赞
- 后台用户审核、公告发布、页面编辑、帖子置顶/精华

## 默认管理员

- 用户名：`admin`
- 密码：`Admin123456!`

请在正式环境中通过 `TENSORHUB_*` 环境变量覆盖默认账号与密钥。
