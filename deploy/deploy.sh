#!/usr/bin/env bash
# ============================================
# TensorHub Community - Production Deployment
# Domain: tensorhub.cn | Server: 159.65.97.63
# ============================================
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*"; }

DOMAIN="tensorhub.cn"
SERVER_IP="159.65.97.63"
PROJECT_DIR="/opt/tensorhub"

# ============================================
# Step 0: Check prerequisites
# ============================================
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    for cmd in ssh docker git; do
        if ! command -v "$cmd" &> /dev/null; then
            log_error "$cmd is not installed locally."
            exit 1
        fi
    done
    
    log_ok "All local prerequisites met."
}

# ============================================
# Step 1: Initial server setup
# ============================================
server_setup() {
    log_info "Setting up server at $SERVER_IP..."
    
    ssh root@"$SERVER_IP" << 'REMOTE_SCRIPT'
set -e

echo "[1/5] Updating system packages..."
apt-get update && apt-get upgrade -y

echo "[2/5] Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "Docker installed successfully."
else
    echo "Docker already installed."
fi

echo "[3/5] Installing Docker Compose..."
if ! docker compose version &> /dev/null; then
    apt-get install -y docker-compose-plugin
else
    echo "Docker Compose already installed."
fi

echo "[4/5] Installing Certbot..."
apt-get install -y certbot

echo "[5/5] Creating project directory..."
mkdir -p /opt/tensorhub/uploads
mkdir -p /var/www/certbot

echo "Server setup complete!"
REMOTE_SCRIPT

    log_ok "Server setup complete."
}

# ============================================
# Step 2: Deploy application
# ============================================
deploy_app() {
    log_info "Deploying application to $SERVER_IP..."
    
    # Copy project files to server
    log_info "Syncing project files..."
    rsync -avz --delete \
        --exclude='.git' \
        --exclude='node_modules' \
        --exclude='__pycache__' \
        --exclude='.env' \
        --exclude='uploads/' \
        --exclude='*.pyc' \
        --exclude='.pytest_cache' \
        --exclude='backend/.env' \
        ./ "root@$SERVER_IP:$PROJECT_DIR/"
    
    log_ok "Files synced."
}

# ============================================
# Step 3: Configure environment
# ============================================
configure_env() {
    log_info "Configuring environment on server..."
    
    ssh root@"$SERVER_IP" << 'REMOTE_SCRIPT'
set -e
cd /opt/tensorhub

if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.production.example .env
    
    # Generate secure passwords
    DB_PASSWORD=$(openssl rand -hex 16)
    JWT_SECRET=$(openssl rand -hex 32)
    ADMIN_PASSWORD=$(openssl rand -hex 12)
    
    sed -i "s/YOUR_SECURE_DB_PASSWORD/$DB_PASSWORD/g" .env
    sed -i "s/YOUR_RANDOM_SECRET_KEY_HERE/$JWT_SECRET/g" .env
    sed -i "s/YOUR_SECURE_ADMIN_PASSWORD/$ADMIN_PASSWORD/g" .env
    
    echo ""
    echo "============================================"
    echo "  IMPORTANT: Save these credentials!"
    echo "============================================"
    echo "  Database password: $DB_PASSWORD"
    echo "  JWT Secret:       $JWT_SECRET"
    echo "  Admin password:   $ADMIN_PASSWORD"
    echo "============================================"
    echo ""
else
    echo ".env already exists, skipping."
fi
REMOTE_SCRIPT

    log_ok "Environment configured."
}

# ============================================
# Step 4: Obtain SSL certificate
# ============================================
obtain_cert() {
    log_info "Obtaining SSL certificate for $DOMAIN..."
    
    # First, start a temporary nginx for certbot
    ssh root@"$SERVER_IP" << REMOTE_SCRIPT
set -e
cd /opt/tensorhub

# Create temporary nginx config for certbot
cat > /tmp/certbot-nginx.conf << 'NGINX_CONF'
server {
    listen 80;
    server_name tensorhub.cn www.tensorhub.cn;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }
}
NGINX_CONF

# Run temporary nginx for cert verification
docker rm -f certbot-nginx 2>/dev/null || true
docker run -d --name certbot-nginx \
    -p 80:80 \
    -v /tmp/certbot-nginx.conf:/etc/nginx/conf.d/default.conf:ro \
    -v /var/www/certbot:/var/www/certbot:ro \
    nginx:alpine

sleep 3

# Obtain certificate
docker rm -f certbot-client 2>/dev/null || true
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

# Clean up temporary nginx
docker rm -f certbot-nginx

echo "SSL certificate obtained successfully!"
REMOTE_SCRIPT

    log_ok "SSL certificate obtained."
}

# ============================================
# Step 5: Build and start services
# ============================================
start_services() {
    log_info "Building and starting services..."
    
    ssh root@"$SERVER_IP" << 'REMOTE_SCRIPT'
set -e
cd /opt/tensorhub

echo "Building Docker images..."
docker compose -f docker-compose.prod.yml build

echo "Starting services..."
docker compose -f docker-compose.prod.yml up -d

echo "Waiting for services to be healthy..."
sleep 15

echo "Running database migrations..."
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head || true

echo ""
echo "Service status:"
docker compose -f docker-compose.prod.yml ps

echo ""
echo "============================================"
echo "  Deployment complete!"
echo "  Site: https://tensorhub.cn"
echo "  API:  https://tensorhub.cn/api"
echo "============================================"
REMOTE_SCRIPT

    log_ok "Services started."
}

# ============================================
# Step 6: Health check
# ============================================
health_check() {
    log_info "Running health check..."
    sleep 10
    
    if curl -sf "https://$DOMAIN/api/auth/session" > /dev/null 2>&1; then
        log_ok "Backend is healthy!"
    elif curl -sf "http://$SERVER_IP/api/auth/session" > /dev/null 2>&1; then
        log_warn "Backend responds on HTTP but HTTPS may not be fully set up yet."
    else
        log_warn "Backend not yet responding. Wait a minute and check manually."
    fi
}

# ============================================
# Main menu
# ============================================
usage() {
    echo "TensorHub Community - Deployment Tool"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  setup      - Initial server setup (install Docker, Certbot, etc.)"
    echo "  deploy     - Deploy and start all services"
    echo "  cert       - Obtain/renew SSL certificate"
    echo "  restart    - Restart all services"
    echo "  stop       - Stop all services"
    echo "  logs       - View service logs"
    echo "  status     - Check service status"
    echo "  full       - Full deployment (setup + deploy + cert + start)"
    echo "  help       - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 full          # First-time full deployment"
    echo "  $0 deploy        # Update and redeploy after code changes"
    echo "  $0 logs          # Check logs"
}

case "${1:-}" in
    setup)
        check_prerequisites
        server_setup
        ;;
    deploy)
        check_prerequisites
        deploy_app
        configure_env
        start_services
        health_check
        ;;
    cert)
        check_prerequisites
        obtain_cert
        ;;
    restart)
        ssh root@"$SERVER_IP" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml restart"
        ;;
    stop)
        ssh root@"$SERVER_IP" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml down"
        ;;
    logs)
        ssh root@"$SERVER_IP" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml logs -f --tail=100"
        ;;
    status)
        ssh root@"$SERVER_IP" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml ps"
        ;;
    full)
        check_prerequisites
        server_setup
        deploy_app
        configure_env
        start_services
        sleep 15
        obtain_cert
        ssh root@"$SERVER_IP" "cd $PROJECT_DIR && docker compose -f docker-compose.prod.yml restart nginx"
        health_check
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        log_error "Unknown command: ${1:-}"
        usage
        exit 1
        ;;
esac