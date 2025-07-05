#!/bin/bash

# Newsletter GPT Installation Script
# Production deployment automation

set -e

echo "🚀 Newsletter GPT Installation Script"
echo "======================================"

# Configuration
APP_NAME="newsletter-gpt"
APP_USER="newsletter-gpt"
APP_DIR="/opt/newsletter-gpt"
SERVICE_NAME="newsletter-gpt"
PYTHON_VERSION="3.11"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

# Check Ubuntu version
if ! command -v lsb_release &> /dev/null; then
    log_error "lsb_release command not found. Are you running Ubuntu?"
    exit 1
fi

UBUNTU_VERSION=$(lsb_release -rs)
log_info "Running on Ubuntu $UBUNTU_VERSION"

# Step 1: Update system
log_info "Step 1: Updating system packages..."
apt update && apt upgrade -y

# Step 2: Install system dependencies
log_info "Step 2: Installing system dependencies..."
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    git \
    curl \
    sqlite3 \
    supervisor \
    nginx \
    certbot \
    python3-certbot-nginx \
    fail2ban \
    ufw \
    htop \
    tree \
    jq

# Step 3: Create application user
log_info "Step 3: Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false -d $APP_DIR $APP_USER
    log_info "Created user: $APP_USER"
else
    log_warn "User $APP_USER already exists"
fi

# Step 4: Create application directory
log_info "Step 4: Creating application directory..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/backups
mkdir -p $APP_DIR/digests

# Step 5: Clone or copy application code
log_info "Step 5: Setting up application code..."
if [ -d "/tmp/newsletter-gpt" ]; then
    log_info "Copying application files from /tmp/newsletter-gpt..."
    cp -r /tmp/newsletter-gpt/* $APP_DIR/
else
    log_info "Please copy your application files to $APP_DIR"
    read -p "Press Enter when ready to continue..."
fi

# Step 6: Create Python virtual environment
log_info "Step 6: Creating Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

# Step 7: Install Python dependencies
log_info "Step 7: Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 8: Set up environment file
log_info "Step 8: Setting up environment configuration..."
if [ ! -f "$APP_DIR/.env" ]; then
    cat > $APP_DIR/.env << 'EOF'
# Newsletter GPT Configuration
# Copy this file and fill in your actual values

# Email Configuration
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# OpenRouter API (for Gemini)
OPENROUTER_API_KEY=your_openrouter_api_key

# Notion Integration
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Database Configuration
NEWSLETTER_DB_PATH=newsletter_data.db

# Logging Configuration
LOG_LEVEL=INFO
EOF
    log_warn "Please edit $APP_DIR/.env with your actual configuration values"
fi

# Step 9: Set up systemd service
log_info "Step 9: Setting up systemd service..."
cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=Newsletter GPT Automation Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
ExecStart=$APP_DIR/venv/bin/python app.py start
ExecReload=/bin/kill -HUP \$MAINPID
KillMode=mixed
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$APP_DIR

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

[Install]
WantedBy=multi-user.target
EOF

# Step 10: Set up log rotation
log_info "Step 10: Setting up log rotation..."
cat > /etc/logrotate.d/$SERVICE_NAME << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 $APP_USER $APP_USER
    postrotate
        systemctl reload $SERVICE_NAME
    endscript
}
EOF

# Step 11: Set up backup script
log_info "Step 11: Setting up backup script..."
cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
# Newsletter GPT Backup Script

BACKUP_DIR="/opt/newsletter-gpt/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_FILE="/opt/newsletter-gpt/newsletter_data.db"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
if [ -f "$DB_FILE" ]; then
    cp "$DB_FILE" "$BACKUP_DIR/newsletter_data_$TIMESTAMP.db"
    echo "Database backed up to $BACKUP_DIR/newsletter_data_$TIMESTAMP.db"
fi

# Backup logs
tar -czf "$BACKUP_DIR/logs_$TIMESTAMP.tar.gz" -C /opt/newsletter-gpt logs/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
EOF

chmod +x $APP_DIR/backup.sh

# Step 12: Set up cron job for backups
log_info "Step 12: Setting up backup cron job..."
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * $APP_DIR/backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -u $APP_USER -

# Step 13: Set permissions
log_info "Step 13: Setting file permissions..."
chown -R $APP_USER:$APP_USER $APP_DIR
chmod +x $APP_DIR/app.py
chmod 600 $APP_DIR/.env

# Step 14: Configure firewall
log_info "Step 14: Configuring firewall..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Step 15: Enable and start services
log_info "Step 15: Enabling and starting services..."
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl enable fail2ban

# Step 16: Initialize database
log_info "Step 16: Initializing database..."
sudo -u $APP_USER $APP_DIR/venv/bin/python -c "
from processors.sqlite_manager import SQLiteManager
db = SQLiteManager()
db.connect()
db.create_tables()
db.disconnect()
print('Database initialized successfully')
"

# Step 17: Test installation
log_info "Step 17: Testing installation..."
if sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/app.py test-components; then
    log_info "✅ Component tests passed"
else
    log_error "❌ Component tests failed"
    log_warn "Please check your .env configuration"
fi

# Final steps
log_info "🎉 Installation completed!"
echo ""
echo "Next steps:"
echo "1. Edit $APP_DIR/.env with your actual configuration"
echo "2. Test the application: systemctl start $SERVICE_NAME"
echo "3. Check logs: journalctl -u $SERVICE_NAME -f"
echo "4. Enable auto-start: systemctl enable $SERVICE_NAME"
echo ""
echo "Useful commands:"
echo "- Start service: systemctl start $SERVICE_NAME"
echo "- Stop service: systemctl stop $SERVICE_NAME"
echo "- Restart service: systemctl restart $SERVICE_NAME"
echo "- Check status: systemctl status $SERVICE_NAME"
echo "- View logs: journalctl -u $SERVICE_NAME -f"
echo "- Test components: sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/app.py test-components"
echo "- Manual daily job: sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/app.py test-daily"
echo "- Manual weekly job: sudo -u $APP_USER $APP_DIR/venv/bin/python $APP_DIR/app.py test-weekly"
echo ""
log_info "Installation complete! 🚀" 