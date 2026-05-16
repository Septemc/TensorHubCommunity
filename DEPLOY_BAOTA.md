# TensorHub Community - 宝塔面板部署指南

> **域名**: community.tensorhub.cn  
> **服务器 IP**: 159.65.97.63  
> **前端路径**: /www/wwwroot/community.tensorhub.cn  
> **项目根目录**: /www/wwwroot/TensorHubCommunity（git clone）  

---

## 目录

1. [前置条件](#1-前置条件)
2. [DNS 配置](#2-dns-配置)
3. [宝塔面板准备](#3-宝塔面板准备)
4. [快速部署](#4-快速部署)
5. [手动部署](#5-手动部署)
6. [宝塔 Nginx 配置](#6-宝塔-nginx-配置)
7. [SSL 证书](#7-ssl-证书)
8. [运维管理](#8-运维管理)
9. [故障排查](#9-故障排查)

---

## 1. 前置条件

- 服务器已安装宝塔面板（推荐 7.9+）
- 宝塔面板中已安装 Nginx
- 本地安装了 `ssh`、`git`、`node`、`rsync`
- 域名 `community.tensorhub.cn` 的管理权限

---

## 2. DNS 配置

在你的域名管理后台添加以下 DNS 记录：

| 类型 | 主机记录 | 记录值 | TTL |
|------|---------|--------|-----|
| **A** | `community` | `159.65.97.63` | 600 |

> ⚠️ DNS 生效通常需要几分钟到数小时，确认生效后再继续：
> ```bash
> ping community.tensorhub.cn
> ```
> 应解析到 `159.65.97.63`。

---

## 3. 宝塔面板准备

### 3.1 安装必要软件

在宝塔面板中：
1. **软件商店** → 安装 **Nginx**（如未安装）
2. **软件商店** → 安装 **Docker 管理器**（如未安装）

### 3.2 创建站点

1. 宝塔面板 → **网站** → **添加站点**
2. 域名填 `community.tensorhub.cn`
3. 根目录设为 `/www/wwwroot/community.tensorhub.cn`
4. PHP 版本选 **纯静态**
5. 点击提交

### 3.3 在服务器上克隆项目

```bash
ssh root@159.65.97.63
cd /www/wwwroot
git clone https://github.com/Septemc/TensorHubCommunity.git
cd TensorHubCommunity

# 创建上传目录
mkdir -p uploads
chmod 777 uploads
```

---

## 4. 快速部署

```bash
# 克隆项目到本地（如果还没克隆）
git clone https://github.com/Septemc/TensorHubCommunity.git
cd TensorHubCommunity

# 给部署脚本添加执行权限
chmod +x deploy/deploy.baota.sh

# 执行完整部署
./deploy/deploy.baota.sh full
```

`full` 命令会自动完成：
1. ✅ 初始化服务器（安装 Docker、创建目录）
2. ✅ 生成安全密码
3. ✅ 同步项目文件到服务器
4. ✅ 配置环境变量
5. ✅ 本地构建前端并同步到站点目录
6. ✅ 构建并启动后端 Docker 容器
7. ✅ 运行数据库迁移
8. ✅ 健康检查

> **⚠️ 请务必保存脚本输出的密码信息！**

部署完成后，还需要在宝塔面板中配置 Nginx 和 SSL 证书（见下方）。

---

## 5. 手动部署

### 5.1 配置服务器

```bash
ssh root@159.65.97.63

# 安装 Docker（如果宝塔未安装）
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# 安装 Docker Compose 插件
apt-get install -y docker-compose-plugin

# 克隆项目
cd /www/wwwroot
git clone https://github.com/Septemc/TensorHubCommunity.git
cd TensorHubCommunity

# 创建上传目录
mkdir -p uploads
chmod 777 uploads

exit
```

### 5.2 配置环境变量

```bash
ssh root@159.65.97.63

cd /www/wwwroot/TensorHubCommunity
cp .env.baota.example .env
nano .env
```

**必须修改的配置项：**

| 环境变量 | 说明 | 生成方式 |
|----------|------|---------|
| `POSTGRES_PASSWORD` | 数据库密码 | `openssl rand -hex 16` |
| `TENSORHUB_DATABASE_URL` | 数据库连接串（密码需同步） | 替换密码部分 |
| `TENSORHUB_JWT_SECRET_KEY` | JWT 密钥 | `python3 -c "import secrets; print(secrets.token_hex(32))"` |
| `TENSORHUB_BOOTSTRAP_ADMIN_PASSWORD` | 管理员密码 | 设置一个强密码 |
| `TENSORHUB_COOKIE_SECURE` | Cookie 安全标志 | 必须设为 `true` |
| `TENSORHUB_COOKIE_DOMAIN` | Cookie 域名 | `community.tensorhub.cn` |

### 5.3 构建前端

```bash
cd frontend
npm install
npm run build

# 同步到服务器站点目录
rsync -avz --delete dist/ root@159.65.97.63:/www/wwwroot/community.tensorhub.cn/
```

### 5.4 启动后端

```bash
ssh root@159.65.97.63

cd /www/wwwroot/TensorHubCommunity

# 构建并启动
docker compose -f docker-compose.baota.yml up -d --build

# 运行数据库迁移
docker compose -f docker-compose.baota.yml exec backend alembic upgrade head

# 查看状态
docker compose -f docker-compose.baota.yml ps
```

---

## 6. 宝塔 Nginx 配置

### 6.1 方法一：通过宝塔面板修改（推荐）

1. 宝塔面板 → **网站** → 点击站点名 `community.tensorhub.cn`
2. 点击 **配置文件**
3. 删除全部内容，替换为项目中 `deploy/nginx/baota_default.conf` 的内容
4. 点击 **保存**
5. 重启 Nginx

### 6.2 方法二：直接复制配置文件

```bash
# 在服务器上
scp /www/wwwroot/TensorHubCommunity/deploy/nginx/baota_default.conf /www/server/panel/vhost/nginx/community.tensorhub.cn.conf
nginx -t && nginx -s reload
```

### 6.3 配置要点说明

宝塔 Nginx 配置的核心要点：

| 配置项 | 说明 |
|--------|------|
| `location /api/` | 反向代理到后端 `http://127.0.0.1:8100` |
| `location /uploads/` | 映射到 `/www/wwwroot/TensorHubCommunity/uploads/` |
| `location /` | SPA 回退，所有前端路由返回 `index.html` |
| `location /assets/` | 静态资源长缓存 |
| HTTP→HTTPS | 由宝塔面板管理（申请SSL后自动添加） |

### 6.4 ⚠️ SSL 证书配置后的重要提醒

在宝塔面板申请 SSL 证书后，会自动在配置文件中生成 443 端口的 server 块。**你必须确保 443 server 块中也包含以下 location 配置**：

```nginx
# 在 443 server 块中添加：
location /api/ {
    proxy_pass http://127.0.0.1:8100/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 120s;
    proxy_connect_timeout 10s;
}

location /uploads/ {
    alias /www/wwwroot/TensorHubCommunity/uploads/;
    expires 7d;
    add_header Cache-Control "public, immutable";
}

location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

location / {
    try_files $uri $uri/ /index.html;
}
```

---

## 7. SSL 证书

### 通过宝塔面板申请（推荐）

1. 宝塔面板 → **网站** → 点击站点名
2. 点击 **SSL** 标签
3. 选择 **Let's Encrypt**
4. 勾选 `community.tensorhub.cn`
5. 点击 **申请**
6. 开启 **强制 HTTPS**

> 宝塔面板会自动续期 Let's Encrypt 证书。

---

## 8. 运维管理

### 8.1 部署脚本命令

```bash
./deploy/deploy.baota.sh full        # 完整首次部署
./deploy/deploy.baota.sh deploy      # 代码更新后重新部署
./deploy/deploy.baota.sh build-fe    # 仅构建前端并同步
./deploy/deploy.baota.sh start       # 启动后端服务
./deploy/deploy.baota.sh stop        # 停止后端服务
./deploy/deploy.baota.sh restart     # 重启后端服务
./deploy/deploy.baota.sh logs        # 查看后端日志
./deploy/deploy.baota.sh status      # 查看服务状态
./deploy/deploy.baota.sh db-backup   # 备份数据库
./deploy/deploy.baota.sh nginx       # 显示 Nginx 配置指引
```

### 8.2 更新部署（代码变更后）

在服务器上拉取最新代码，然后重新部署：
```bash
ssh root@159.65.97.63
cd /www/wwwroot/TensorHubCommunity
git pull

# 重新构建并启动后端
docker compose -f docker-compose.baota.yml up -d --build
sleep 15
docker compose -f docker-compose.baota.yml exec backend alembic upgrade head
```

前端也需要重新构建：
```bash
# 在本地
cd frontend
npm install
npm run build
rsync -avz --delete dist/ root@159.65.97.63:/www/wwwroot/community.tensorhub.cn/
```

### 8.3 仅更新前端

```bash
cd frontend
npm run build
rsync -avz --delete dist/ root@159.65.97.63:/www/wwwroot/community.tensorhub.cn/
```

### 8.4 查看后端日志

```bash
ssh root@159.65.97.63
cd /www/wwwroot/TensorHubCommunity

# 实时日志
docker compose -f docker-compose.baota.yml logs -f backend

# 最近100行
docker compose -f docker-compose.baota.yml logs --tail=100 backend
```

### 8.5 数据库备份

```bash
ssh root@159.65.97.63
cd /www/wwwroot/TensorHubCommunity

# 创建备份
docker compose -f docker-compose.baota.yml exec db \
  pg_dump -U postgres tensorhub > /tmp/backup_$(date +%Y%m%d_%H%M%S).sql

# 恢复备份
cat /tmp/backup_20240101_120000.sql | \
  docker compose -f docker-compose.baota.yml exec -T db \
  psql -U postgres tensorhub
```

### 8.6 数据库迁移

当后端模型有变更时：

```bash
# 本地生成迁移文件
cd backend
alembic revision --autogenerate -m "描述"

# 在服务器上执行迁移
ssh root@159.65.97.63
cd /www/wwwroot/TensorHubCommunity
docker compose -f docker-compose.baota.yml exec backend alembic upgrade head
```

---

## 9. 故障排查

### Q: 网站无法访问

```bash
ssh root@159.65.97.63

# 检查后端服务
cd /www/wwwroot/TensorHubCommunity
docker compose -f docker-compose.baota.yml ps

# 检查 Nginx 配置
nginx -t

# 检查端口监听
ss -tlnp | grep -E '80|443|8100'
```

### Q: API 返回 502 Bad Gateway

- 后端容器未启动或未就绪
- 检查：`docker compose -f docker-compose.baota.yml logs backend`

### Q: 前端页面空白

- 检查 `index.html` 是否在站点目录：`ls /www/wwwroot/community.tensorhub.cn/`
- 检查 Nginx 配置的 `root` 路径是否正确
- 检查浏览器控制台是否有资源加载错误

### Q: 上传文件 404

- 确认 `/www/wwwroot/TensorHubCommunity/uploads/` 目录存在且有权限
- 确认 Nginx 配置中 `/uploads/` 路径正确映射

### Q: 端口 8100 被占用

如果出现 `Bind for 127.0.0.1:8100 failed: port is already allocated` 错误：

```bash
# 方法1：停止所有 docker-compose 服务
cd /www/wwwroot/TensorHubCommunity
docker compose down          # 停止原始 docker-compose.yml 的服务
docker compose -f docker-compose.baota.yml down  # 停止 baota 版服务

# 方法2：查找并杀死占用端口的进程
ss -tlnp | grep :8100
kill <PID>

# 然后重新启动
docker compose -f docker-compose.baota.yml up -d
```

### Q: 数据库连接失败

- 检查 `.env` 中 `POSTGRES_PASSWORD` 和 `TENSORHUB_DATABASE_URL` 密码一致
- 检查 db 容器是否正常：`docker compose -f docker-compose.baota.yml ps`

---

## 架构概览

```
Internet → 宝塔 Nginx (80/443)
              ├── /            → /www/wwwroot/community.tensorhub.cn (Vue SPA 前端)
              ├── /assets/      → 静态资源（长缓存）
              ├── /uploads/     → /www/wwwroot/TensorHubCommunity/uploads/
              └── /api/        → http://127.0.0.1:8100 (Docker 后端)

服务器文件布局:
  /www/wwwroot/TensorHubCommunity/       ← git clone 项目（后端代码 + Docker 配置）
  /www/wwwroot/community.tensorhub.cn/  ← 前端构建产物（npm run build 输出）

Docker Network:
  backend:8000 → db:5432 (PostgreSQL)