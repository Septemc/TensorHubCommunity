# TensorHubCommunity

单仓实现的 TensorHub 社区 MVP，包含：

- `backend/`：FastAPI + SQLAlchemy async + PostgreSQL
- `frontend/`：Vue 3 + TypeScript + Vite + Pinia + Element Plus
- `deploy/`：Nginx 配置

## 启动建议

1. 复制根目录 `.env.example` 为 `.env` 并修改 `TENSORHUB_*` 配置项。
2. 启动 PostgreSQL。
3. 后端执行 `pip install -r requirements.txt` 后运行 `uvicorn app.main:app --reload`。
4. 前端执行 `npm install` 后运行 `npm run dev`。

## 默认能力

- 实名注册、登录、Cookie 鉴权、管理员审核
- 官网首页、团队介绍、公告管理
- 论坛板块、帖子、评论、点赞
- 后台用户审核、公告发布、页面编辑、帖子置顶/精华

## 默认管理员

- 用户名：`admin`
- 密码：`Admin123456!`

请在正式环境中通过 `TENSORHUB_*` 环境变量覆盖默认账号与密钥。
