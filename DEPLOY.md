# TensorHub Community 生产部署指南

> **域名**: tensorhub.cn  
> **服务器 IP**: 159.65.97.63

---

## 目录

1. [前置条件](#1-前置条件)
2. [DNS 配置](#2-dns-配置)
3. [快速部署（推荐）](#3-快速部署推荐)
4. [手动部署](#4-手动部署)
5. [配置说明](#5-配置说明)
6. [运维管理](#6-运维管理)
7. [故障排查](#7-故障排查)

---

## 1. 前置条件

- 一台运行 Ubuntu 20.04+ 的服务器（IP: 159.65.97.63）
- 域名 `tensorhub.cn` 的管理权限
- 本地安装了 `ssh`、`docker`、`git`、`rsync`
- 能通过 SSH 登录服务器（建议使用 root 或有 sudo 权限的用户）

---

## 2. DNS 配置

在你的域名管理后台添加以下 DNS 记录：

| 类型 | 主机记录 | 记录值 | TTL |
|------|---------|--------|-----|
| A | `@` | `159.65.97.63` | 600 |
| A | `www` | `159.65.97.63` | 600 |

> ⚠️ DNS 生效通常需要几分钟到数小时，确认生效后再继续：
> ```bash
> ping tensorhub.cn
> ping www.tensorhub.cn
> ```
> 两个地址都应解析到 `159.65.97.63`。

---

## 3. 快速部署（推荐）

项目提供了自动化部署脚本，一键完成所有配置：

```bash
# 克隆项目
git clone git@github.com:Septemc/TensorHubCommunity.git
cd TensorHubCommunity

# 给部署脚本添加执行权限
chmod +x deploy/deploy.sh

# 执行完整部署（首次部署推荐）
./deploy/deploy.sh full
```

`full` 命令将自动完成：
1. ✅ 服务器初始化（安装 Docker、Docker Compose、Certbot）
2. ✅ 同步项目文件到服务器
3. ✅ 生成安全的环境变量（数据库密码、JWT密钥、管理员密码）
4. ✅ 构建并启动所有 Docker 服务
5. ✅ 申请 Let's Encrypt SSL 证书
6. ✅ 重启 Nginx 并启用 HTTPS
7. ✅ 健康检查

> **⚠️ 请务必保存部署脚本输出的密码信息！**

---

## 4. 手动部署

如果希望手动操作，按以下步骤执行：

### 4.1 服务器初始化

```bash
# SSH 登录服务器
ssh root@159.65.97.63

# 更新系统
apt-get update && apt-get upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 安装 Docker Compose 插件
apt-get install -y docker-compose-plugin

# 安装 Certbot
apt-get install -y certbot

# 创建项目目录
mkdir -p /opt/tensorhub/uploads /var/www/certbot

# 退出 SSH
exit
```

### 4.2 同步项目文件

```bash
# 在本地执行
rsync -avz --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='.env' \
  --exclude='uploads/' \
  --exclude='*.pyc' \
  ./ root@159.65.97.63:/opt/tensorhub/
```

### 4.3 配置环境变量

```bash
ssh root@159.65.97.63

cd /opt/tensorhub

# 复制环境变量模板
cp .env.production.example .env

# 编辑 .env，填入真实的密码和密钥
nano .env
```

**必须修改的配置项：**

| 环境变量 | 说明 | 示例 |
|----------|------|------|
| `POSTGRES_PASSWORD` | 数据库密码 | 生成方式: `openssl rand -hex 16` |
| `TENSORHUB_DATABASE_URL` | 数据库连接串 | 将密码同步替换 |
| `TENSORHUB_JWT_SECRET_KEY` | JWT 签名密钥 | 生成方式: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `TENSORHUB_BOOTSTRAP_ADMIN_PASSWORD` | 管理员初始密码 | 设置一个强密码 |
| `TENSORHUB_COOKIE_SECURE` | Cookie 安全标志 | 生产环境必须设为 `true` |
| `TENSORHUB_COOKIE_DOMAIN` | Cookie 域名 | `tensorhub.cn` |

> ⚠️ **重要**: `TENSORHUB_DATABASE_URL` 中的密码必须与 `POSTGRES_PASSWORD` 一致！

### 4.4 初次申请 SSL 证书

```bash
# 在服务器上执行

# 启动临时 Nginx 用于 ACME 验证
docker run -d --name certbot-nginx \
  -p 80:80 \
  -v /opt/tensorhub/deploy/nginx/certbot-only.conf:/etc/nginx/conf.d/default.conf:ro \
  -v /var/www/certbot:/var/www/certbot:ro \
  nginx:alpine

sleep 3

# 申请证书
docker run --name certbot-client \
  -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot certonly \
  -w /var/www/certbot \
  -d tensorhub.cn \
  -d www.tensorhub.cn \
  --email admin@tensorhub.cn \
  --agree-tos \
  --no-eff-email \
  --non-interactive

# 清理临时容器
docker rm -f certbot-nginx certbot-client
```

### 4.5 构建并启动服务

```bash
cd /opt/tensorhub

# 构建镜像
docker compose -f docker-compose.prod.yml build

# 启动服务
docker compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker compose -f docker-compose.prod.yml ps

# 查看日志
docker compose -f docker-compose.prod.yml logs -f
```

### 4.6 数据库迁移

```bash
# 运行 Alembic 数据库迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

### 4.7 验证部署

```bash
# 检查后端健康状态
curl https://tensorhub.cn/api/auth/session

# 检查前端是否响应
curl -I https://tensorhub.cn/
```

---

## 5. 配置说明

### 5.1 架构概览

```
Internet → Nginx (80/443) → Frontend (80, 静态文件)
                           → Backend (8000, API)
                           → /uploads (静态上传文件)
                           → Certbot (SSL自动续期)

Backend → PostgreSQL (5432)
```

### 5.2 Docker 服务说明

| 服务 | 说明 | 端口 |
|------|------|------|
| `nginx` | 反向代理 + SSL + 静态文件 | 80, 443 |
| `frontend` | Vue3 SPA (Nginx 容器) | 内部 80 |
| `backend` | FastAPI + Gunicorn | 内部 8000 |
| `db` | PostgreSQL 16 | 内部 5432 |
| `certbot` | SSL 证书自动续期 | 无 |

### 5.3 网络隔离

- `internal` 网络: 仅 `db` 和 `backend` 可访问，数据库不对外暴露
- `proxy` 网络: `nginx`、`frontend`、`backend` 互相通信

### 5.4 数据持久化

| 卷名 | 挂载点 | 说明 |
|------|--------|------|
| `postgres_data` | `/var/lib/postgresql/data` | 数据库数据 |
| `uploads` | `/app/uploads` / `/uploads` | 用户上传文件 |
| `certbot_conf` | `/etc/letsencrypt` | SSL 证书 |
| `certbot_www` | `/var/www/certbot` | ACME 验证文件 |

---

## 6. 运维管理

### 6.1 部署脚本命令

```bash
./deploy/deploy.sh full      # 完整首次部署
./deploy/deploy.sh deploy    # 代码更新后重新部署
./deploy/deploy.sh cert      # 重新申请SSL证书
./deploy/deploy.sh restart   # 重启所有服务
./deploy/deploy.sh stop      # 停止所有服务
./deploy/deploy.sh logs      # 查看实时日志
./deploy/deploy.sh status    # 查看服务状态
```

### 6.2 更新部署（代码变更后）

```bash
# 本地拉取最新代码
git pull

# 重新部署到服务器
./deploy/deploy.sh deploy
```

### 6.3 查看日志

```bash
# 在服务器上
cd /opt/tensorhub

# 查看所有日志
docker compose -f docker-compose.prod.yml logs -f

# 查看特定服务日志
docker compose -f docker-compose.prod.yml logs -f backend
docker compose -f docker-compose.prod.yml logs -f nginx

# 查看最近100行
docker compose -f docker-compose.prod.yml logs --tail=100 backend
```

### 6.4 数据库备份

```bash
# 在服务器上创建备份
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U postgres tensorhub > backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
cat backup_20240101_120000.sql | \
  docker compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres tensorhub
```

### 6.5 SSL 证书续期

Let's Encrypt 证书有效期为 90 天，`certbot` 容器会自动续期。

手动续期测试：
```bash
docker compose -f docker-compose.prod.yml exec certbot certbot renew --dry-run
```

### 6.6 数据库迁移

当后端模型有变更时：
```bash
# 生成迁移文件（本地开发时）
cd backend
alembic revision --autogenerate -m "描述"

# 在服务器上执行迁移
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

---

## 7. 故障排查

### 7.1 常见问题

**Q: 网站无法访问**
```bash
# 检查服务状态
docker compose -f docker-compose.prod.yml ps

# 检查 Nginx 日志
docker compose -f docker-compose.prod.yml logs nginx

# 检查端口监听
ss -tlnp | grep -E '80|443|8000'
```

**Q: SSL 证书申请失败**
- 确认 DNS 已指向服务器 IP
- 确认 80 端口未被占用
- 确认防火墙放行 80/443 端口

**Q: 后端 500 错误**
```bash
# 查看 backend 日志
docker compose -f docker-compose.prod.yml logs backend
```

**Q: 数据库连接失败**
- 检查 `.env` 中 `POSTGRES_PASSWORD` 和 `TENSORHUB_DATABASE_URL` 密码是否一致
- 检查 db 容器是否正常运行

### 7.2 防火墙配置

```bash
# 在服务器上开放必要端口
ufw allow 80/tcp     # HTTP
ufw allow 443/tcp    # HTTPS
ufw allow 22/tcp     # SSH
ufw enable
```

### 7.3 重置部署

⚠️ 这将删除所有数据！

```bash
ssh root@159.65.97.63
cd /opt/tensorhub
docker compose -f docker-compose.prod.yml down -v
# -v 会删除所有数据卷（数据库、上传文件、证书）
```

---

## 文件结构

```
TensorHubCommunity/
├── .env.production.example      # 生产环境变量模板
├── docker-compose.prod.yml      # 生产 Docker Compose 配置
├── deploy/
│   ├── deploy.sh                # 自动化部署脚本
│   └── nginx/
│       ├── default.conf         # Nginx 生产配置（SSL + 反向代理）
│       └── certbot-only.conf    # 证书申请阶段临时配置
├── backend/
│   └── Dockerfile               # 后端 Docker 镜像
└── frontend/
    └── Dockerfile               # 前端多阶段构建镜像