#!/usr/bin/env bash
# ============================================
# TensorHub Community - 宝塔面板部署脚本
# 域名: community.tensorhub.cn
# 前端: /www/wwwroot/community.tensorhub.cn
# 后端: /www/wwwroot/TensorHubCommunity (Docker)
# ============================================

set -euo pipefail

# ---- 配置 ----
SERVER="root@159.65.97.63"
REMOTE_DIR="/www/wwwroot/TensorHubCommunity"
FRONTEND_DIR="/www/wwwroot/community.tensorhub.cn"
DOMAIN="community.tensorhub.cn"

# ---- 颜色输出 ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
error() { echo -e "${RED}[ERROR]${NC} $*"; exit 1; }

# ---- 检查依赖 ----
check_deps() {
    info "检查本地依赖..."
    for cmd in ssh rsync docker; do
        command -v "$cmd" &>/dev/null || error "缺少依赖: $cmd"
    done
}

# ---- 生成安全密码 ----
gen_passwords() {
    info "生成安全密码..."
    DB_PASSWORD=$(openssl rand -hex 16)
    JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || openssl rand -hex 32)
    ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d '/+=' | head -c 16)

    DATABASE_URL="postgresql+asyncpg://postgres:${DB_PASSWORD}@db:5432/tensorhub"

    info "数据库密码: ${DB_PASSWORD}"
    info "JWT密钥: ${JWT_SECRET}"
    info "管理员密码: ${ADMIN_PASSWORD}"
    echo ""
    warn "⚠️  请务必保存以上密码！"
    echo ""
}

# ---- 初始化服务器 ----
init_server() {
    info "初始化服务器环境..."
    ssh "$SERVER" bash -s <<'REMOTE_SCRIPT'
set -e

# 安装 Docker（如果未安装）
if ! command -v docker &>/dev/null; then
    echo "[REMOTE] 安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker && systemctl start docker
fi

# 安装 Docker Compose 插件
if ! docker compose version &>/dev/null; then
    echo "[REMOTE] 安装 Docker Compose..."
    apt-get install -y docker-compose-plugin
fi

# 创建目录
echo "[REMOTE] 创建目录..."
mkdir -p /www/wwwroot/TensorHubCommunity/uploads
mkdir -p /www/wwwroot/community.tensorhub.cn

# 设置上传目录权限
chmod 777 /www/wwwroot/TensorHubCommunity/uploads

REMOTE_SCRIPT
    info "服务器初始化完成"
}

# ---- 同步项目文件 ----
sync_files() {
    info "同步项目文件到服务器..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.env' \
        --exclude='dist/' \
        --exclude='*.pyc' \
        --exclude='.vscode' \
        --exclude='.idea' \
        --exclude='logs/' \
        --exclude='uploads/' \
        --exclude='frontend/dist' \
        --exclude='frontend/node_modules' \
        ./ "${SERVER}:${REMOTE_DIR}/"
}

# ---- 配置环境变量 ----
setup_env() {
    info "配置环境变量..."
    if [ -z "${DB_PASSWORD:-}" ]; then
        gen_passwords
    fi

    ssh "$SERVER" bash -s <<REMOTE_SCRIPT
cat > "${REMOTE_DIR}/.env" <<'EOF'
TENSORHUB_APP_ENV=production
TENSORHUB_DEBUG=false
TENSORHUB_DATABASE_URL=${DATABASE_URL}
POSTGRES_USER=postgres
POSTGRES_PASSWORD=${DB_PASSWORD}
TENSORHUB_JWT_SECRET_KEY=${JWT_SECRET}
TENSORHUB_COOKIE_SECURE=true
TENSORHUB_COOKIE_DOMAIN=${DOMAIN}
TENSORHUB_CORS_ORIGINS=["https://${DOMAIN}"]
TENSORHUB_MAX_UPLOAD_SIZE_MB=5
TENSORHUB_BOOTSTRAP_ADMIN_USERNAME=admin
TENSORHUB_BOOTSTRAP_ADMIN_PASSWORD=${ADMIN_PASSWORD}
TENSORHUB_BOOTSTRAP_ADMIN_REAL_NAME=TensorHub Admin
TENSORHUB_BOOTSTRAP_ADMIN_EMAIL=admin@tensorhub.cn
TENSORHUB_BOOTSTRAP_ADMIN_STUDENT_ID=ADMIN0001
TENSORHUB_BOOTSTRAP_ADMIN_MAJOR=System
TENSORHUB_BOOTSTRAP_ADMIN_GENDER=other
EOF
REMOTE_SCRIPT
    info "环境变量配置完成"
}

# ---- 构建前端 ----
build_frontend() {
    info "本地构建前端..."
    cd frontend
    npm install
    npm run build
    cd ..

    info "同步前端构建产物到服务器..."
    rsync -avz --delete \
        frontend/dist/ \
        "${SERVER}:${FRONTEND_DIR}/"
}

# ---- 构建并启动后端 Docker ----
start_backend() {
    info "构建并启动后端服务..."
    ssh "$SERVER" bash -s <<REMOTE_SCRIPT
cd "${REMOTE_DIR}"

# 停止可能占用端口的旧容器（原始 docker-compose.yml 的服务）
if [ -f docker-compose.yml ]; then
    echo "[REMOTE] 停止旧版 docker-compose 服务..."
    docker compose down 2>/dev/null || true
fi

# 也停止 baota 版本的旧容器
docker compose -f docker-compose.baota.yml down 2>/dev/null || true

# 检查并杀死占用 8000 端口的进程
PORT_USER=\$(ss -tlnp | grep ':8000' | head -1)
if [ -n "\$PORT_USER" ]; then
    echo "[REMOTE] 端口 8000 被占用，正在释放..."
    echo "\$PORT_USER"
    PID=\$(echo "\$PORT_USER" | grep -oP 'pid=\K\d+' || echo "")
    if [ -n "\$PID" ]; then
        kill "\$PID" 2>/dev/null || true
        sleep 2
    fi
fi

# 构建后端镜像
docker compose -f docker-compose.baota.yml build

# 启动服务
docker compose -f docker-compose.baota.yml up -d

# 等待数据库就绪
echo "[REMOTE] 等待数据库启动..."
sleep 5

# 运行数据库迁移
docker compose -f docker-compose.baota.yml exec backend alembic upgrade head

# 查看状态
docker compose -f docker-compose.baota.yml ps
REMOTE_SCRIPT
    info "后端服务启动完成"
}

# ---- 配置 Nginx ----
setup_nginx() {
    info "配置 Nginx 站点..."
    warn "请在宝塔面板中操作："
    warn "  1. 网站 → 添加站点 → 域名填 ${DOMAIN}"
    warn "  2. 网站设置 → 配置文件 → 替换为 deploy/nginx/baota_default.conf 内容"
    warn "  3. 网站设置 → SSL → 申请/部署 Let's Encrypt 证书"
    warn "  4. 或直接复制配置文件："
    warn "     scp deploy/nginx/baota_default.conf ${SERVER}:/www/server/panel/vhost/nginx/${DOMAIN}.conf"
    echo ""
}

# ---- 健康检查 ----
health_check() {
    info "健康检查..."
    echo ""

    # 检查后端 API
    info "检查后端 API..."
    if ssh "$SERVER" "curl -sf http://127.0.0.1:8000/api/auth/session" | head -1; then
        info "✅ 后端 API 正常"
    else
        warn "⚠️ 后端 API 暂未响应（可能仍在启动中）"
    fi

    # 检查前端
    info "检查前端访问..."
    if ssh "$SERVER" "test -f ${FRONTEND_DIR}/index.html"; then
        info "✅ 前端文件已就位"
    else
        warn "⚠️ 前端文件未找到"
    fi

    echo ""
    info "============================================"
    info "  部署完成！"
    info "============================================"
    echo ""
    info "  访问地址: https://${DOMAIN}"
    info "  管理员用户: admin"
    info "  管理员密码: ${ADMIN_PASSWORD:-（已设置）}"
    echo ""
    warn "  请确保在宝塔面板中配置 Nginx 和 SSL 证书"
    echo ""
}

# ---- 更新部署 ----
deploy() {
    info "更新部署..."
    build_frontend
    sync_files
    ssh "$SERVER" bash -s <<REMOTE_SCRIPT
cd "${REMOTE_DIR}"
docker compose -f docker-compose.baota.yml build backend
docker compose -f docker-compose.baota.yml up -d backend
docker compose -f docker-compose.baota.yml exec backend alembic upgrade head
docker compose -f docker-compose.baota.yml ps
REMOTE_SCRIPT
    rsync -avz --delete frontend/dist/ "${SERVER}:${FRONTEND_DIR}/"
    info "更新完成！"
}

# ---- 主流程 ----
case "${1:-help}" in
    full)
        check_deps
        init_server
        gen_passwords
        sync_files
        setup_env
        build_frontend
        start_backend
        setup_nginx
        health_check
        ;;
    deploy)
        check_deps
        deploy
        ;;
    init)
        check_deps
        init_server
        ;;
    build-fe)
        build_frontend
        ;;
    start)
        start_backend
        ;;
    stop)
        ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose -f docker-compose.baota.yml down"
        ;;
    restart)
        ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose -f docker-compose.baota.yml restart backend"
        ;;
    logs)
        ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose -f docker-compose.baota.yml logs -f --tail=100 backend"
        ;;
    status)
        ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose -f docker-compose.baota.yml ps"
        ;;
    db-backup)
        ssh "$SERVER" "cd ${REMOTE_DIR} && docker compose -f docker-compose.baota.yml exec db pg_dump -U postgres tensorhub > /tmp/tensorhub_backup_\$(date +%Y%m%d_%H%M%S).sql"
        info "数据库备份已保存到服务器 /tmp/ 目录"
        ;;
    nginx)
        setup_nginx
        ;;
    help|*)
        echo "TensorHub Community - 宝塔面板部署脚本"
        echo ""
        echo "用法: $0 <命令>"
        echo ""
        echo "命令:"
        echo "  full       完整首次部署（推荐）"
        echo "  deploy     更新部署（代码变更后）"
        echo "  init       初始化服务器环境"
        echo "  build-fe   仅构建前端并同步"
        echo "  start      启动后端服务"
        echo "  stop       停止后端服务"
        echo "  restart    重启后端服务"
        echo "  logs       查看后端日志"
        echo "  status     查看服务状态"
        echo "  db-backup  备份数据库"
        echo "  nginx      显示 Nginx 配置指引"
        ;;
esac