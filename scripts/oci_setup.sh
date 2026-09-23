#!/bin/bash
# ==============================================================================
# AI Job Agent - Oracle Cloud (VM.Standard.A1.Flex) VM Automated Setup
# Architecture: Ampere Altra (ARM64 / aarch64)
# Supported OS: Ubuntu 22.04/24.04 LTS, Oracle Linux 8/9
# ==============================================================================
set -euo pipefail

echo "=========================================================="
echo "🚀 Initializing AI Job Agent Setup for Oracle Cloud A1"
echo "   Architecture: $(uname -m)"
echo "=========================================================="

if [ "$EUID" -ne 0 ]; then
  echo "❌ Please run this script with sudo: sudo ./scripts/oci_setup.sh"
  exit 1
fi

REAL_USER="${SUDO_USER:-$USER}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# ------------------------------------------------------------------------------
# 1. Detect Operating System
# ------------------------------------------------------------------------------
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$ID
    OS_VERSION_ID=${VERSION_ID%%.*}
else
    echo "❌ Cannot determine OS from /etc/os-release"
    exit 1
fi

echo "📦 Detected OS: $OS_NAME (Version: $VERSION_ID)"

# ------------------------------------------------------------------------------
# 2. Configure Swap Space (4GB safety cushion for compilation / builds)
# ------------------------------------------------------------------------------
TOTAL_SWAP=$(free -m | awk '/^Swap:/ {print $2}')
if [ "$TOTAL_SWAP" -lt 1024 ]; then
    echo "🔧 Setting up 4GB swapfile for smooth ARM64 container builds..."
    SWAPFILE="/swapfile"
    if [ ! -f "$SWAPFILE" ]; then
        fallocate -l 4G "$SWAPFILE" || dd if=/dev/zero of="$SWAPFILE" bs=1M count=4096
        chmod 600 "$SWAPFILE"
        mkswap "$SWAPFILE"
        swapon "$SWAPFILE"
        if ! grep -q "$SWAPFILE" /etc/fstab; then
            echo "$SWAPFILE none swap sw 0 0" >> /etc/fstab
        fi
        echo "✅ 4GB swap space configured."
    fi
else
    echo "✅ Sufficient swap already configured (${TOTAL_SWAP}MB)."
fi

# ------------------------------------------------------------------------------
# 3. Install Docker & Docker Compose Plugin
# ------------------------------------------------------------------------------
echo "🐳 Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "Installing Docker Engine and Compose plugin for ARM64..."
    if [[ "$OS_NAME" == "ubuntu" || "$OS_NAME" == "debian" ]]; then
        apt-get update
        apt-get install -y ca-certificates curl gnupg lsb-release
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/$OS_NAME/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/$OS_NAME \
          $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
          tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    elif [[ "$OS_NAME" == "ol" || "$OS_NAME" == "rhel" || "$OS_NAME" == "centos" ]]; then
        dnf install -y dnf-utils
        dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi

    systemctl enable --now docker
    usermod -aG docker "$REAL_USER"
    echo "✅ Docker installed and service enabled."
else
    echo "✅ Docker is already installed: $(docker --version)"
fi

# ------------------------------------------------------------------------------
# 4. Configure Host OS Firewall (Oracle Linux / Ubuntu OCI Rules)
# ------------------------------------------------------------------------------
echo "🛡️ Configuring host OS firewall..."

# Handle firewalld (default in Oracle Linux)
if command -v firewall-cmd &> /dev/null && systemctl is-active --quiet firewalld; then
    echo "Configuring firewalld rules..."
    firewall-cmd --permanent --add-port=80/tcp || true
    firewall-cmd --permanent --add-port=443/tcp || true
    firewall-cmd --permanent --add-port=3000/tcp || true
    firewall-cmd --permanent --add-port=4000/tcp || true
    firewall-cmd --reload
    echo "✅ Firewalld ports 80, 443, 3000, 4000 opened."
fi

# Handle ufw (common in Ubuntu)
if command -v ufw &> /dev/null && ufw status | grep -q "Status: active"; then
    echo "Configuring ufw rules..."
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 3000/tcp
    ufw allow 4000/tcp
    ufw reload
    echo "✅ UFW ports 80, 443, 3000, 4000 opened."
fi

# Handle default Oracle Cloud Ubuntu iptables reject rules
if iptables -L INPUT -n | grep -q "REJECT"; then
    echo "Applying iptables rules to bypass OCI default reject filters..."
    iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT || true
    iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT || true
    iptables -I INPUT 1 -p tcp --dport 3000 -j ACCEPT || true
    iptables -I INPUT 1 -p tcp --dport 4000 -j ACCEPT || true
    
    if command -v netfilter-persistent &> /dev/null; then
        netfilter-persistent save || true
    elif [ -d /etc/iptables ]; then
        iptables-save > /etc/iptables/rules.v4 || true
    fi
    echo "✅ Ingress iptables rules applied for 80, 443, 3000, 4000."
fi

# ------------------------------------------------------------------------------
# 5. Generate Initial SSL Certificates (if not already present)
# ------------------------------------------------------------------------------
echo "🔒 Checking SSL certificates..."
mkdir -p "$PROJECT_DIR/nginx/ssl"
if [ ! -f "$PROJECT_DIR/nginx/ssl/fullchain.pem" ]; then
    echo "Generating initial SSL certificates for agent.jobs.shubhamprakash681.in..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
      -keyout "$PROJECT_DIR/nginx/ssl/privkey.pem" \
      -out "$PROJECT_DIR/nginx/ssl/fullchain.pem" \
      -subj "/C=IN/ST=Maharashtra/L=Mumbai/O=AI Job Agent/CN=agent.jobs.shubhamprakash681.in" \
      -addext "subjectAltName=DNS:agent.jobs.shubhamprakash681.in,DNS:localhost,IP:130.210.26.198,IP:127.0.0.1"
    chown -R "$REAL_USER":"$REAL_USER" "$PROJECT_DIR/nginx/ssl"
    echo "✅ SSL certificates generated in ./nginx/ssl/."
else
    echo "✅ SSL certificates already exist."
fi

# ------------------------------------------------------------------------------
# 6. Create Systemd Service for Auto-Restart on VM Boot
# ------------------------------------------------------------------------------
echo "⚙️ Creating systemd service for AI Job Agent..."
cat <<EOF > /etc/systemd/system/ai-job-agent.service
[Unit]
Description=AI Job Agent Production Orchestration (HTTPS)
Requires=docker.service
After=docker.service network-online.target
Wants=network-online.target

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$PROJECT_DIR
User=$REAL_USER
Group=docker
ExecStart=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f docker-compose.yml -f docker-compose.prod.yml down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable ai-job-agent.service
echo "✅ systemd service 'ai-job-agent.service' enabled."

# ------------------------------------------------------------------------------
# 6. Summary and OCI Security List Reminder
# ------------------------------------------------------------------------------
echo ""
echo "=========================================================="
echo "🎉 Setup Complete on Oracle Cloud (VM.Standard.A1.Flex)!"
echo "=========================================================="
echo ""
echo "CRITICAL NEXT STEP: Configure OCI Security List Ingress Rules!"
echo "1. Go to Oracle Cloud Console -> Compute -> Instances -> Click your VM"
echo "2. Under 'Primary VNIC', click your Subnet link"
echo "3. Click your 'Default Security List for ...'"
echo "4. Click 'Add Ingress Rules' and allow:"
echo "   - Source: 0.0.0.0/0 | Protocol: TCP | Destination Port Range: 80"
echo "   - Source: 0.0.0.0/0 | Protocol: TCP | Destination Port Range: 443"
echo "   - Source: 0.0.0.0/0 | Protocol: TCP | Destination Port Range: 3000 (HTTPS Frontend)"
echo "   - Source: 0.0.0.0/0 | Protocol: TCP | Destination Port Range: 4000 (HTTPS Backend API)"
echo ""
echo "To start the application with full HTTPS:"
echo "   1. cp .env.example .env (and configure secrets/keys)"
echo "   2. docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build"
echo "=========================================================="

