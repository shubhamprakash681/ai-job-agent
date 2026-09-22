# Oracle Cloud Infrastructure (OCI) Deployment Guide
## Production Target: `http://agent.jobs.shubhamprakash681.in`

This guide details how to deploy and configure the **AI Job Agent** on an Oracle Cloud Infrastructure (OCI) **`VM.Standard.A1.Flex`** compute instance (Ampere Altra ARM64) mapped to your domain **`agent.jobs.shubhamprakash681.in`**.

---

## 1. Architecture & Domain Overview

- **Compute Instance**: Oracle Cloud `VM.Standard.A1.Flex` (Ampere Altra ARM64 / aarch64)
- **Public IP Address**: `130.210.26.198`
- **Domain Name**: `agent.jobs.shubhamprakash681.in`
- **DNS Provider**: GoDaddy (`domaincontrol.com`)
- **Port Mapping**:
  - `80` (HTTP) &rarr; Nginx reverse proxy &rarr; Next.js Frontend (`3000`)
  - `443` (HTTPS) &rarr; Nginx with SSL (Let's Encrypt)
  - `8000` (FastAPI Backend) &rarr; Bound internally to `127.0.0.1` (proxied server-side via Next.js `/api/...`)
  - `5431` (PostgreSQL) & `6379` (Redis) &rarr; Bound securely to `127.0.0.1`

---

## 2. Step 1: DNS Configuration (GoDaddy)

Ensure the DNS record for your subdomain is active:

1. Log into your **GoDaddy DNS Management Console** for `shubhamprakash681.in`.
2. Verify or add the following **A Record**:

| Type | Name / Host | Value / Target | TTL |
| :--- | :--- | :--- | :--- |
| **A** | `agent.jobs` | `130.210.26.198` | 1/2 Hour (or 600s) |

> [!NOTE]
> Ensure the name is **`agent.jobs`** (singular), which resolves to `agent.jobs.shubhamprakash681.in`.

---

## 3. Step 2: OCI Virtual Cloud Network (VCN) Ingress Rules

In your Oracle Cloud Console, ensure your VCN Security List allows web traffic:

1. Go to **Networking** &rarr; **Virtual Cloud Networks** &rarr; Click your VCN.
2. Under Resources, click **Security Lists** &rarr; Select your **Default Security List for...**.
3. Under **Ingress Rules**, confirm you have rules for ports 80, 443, and 3000:

| Source CIDR | IP Protocol | Destination Port Range | Description |
| :--- | :--- | :--- | :--- |
| `0.0.0.0/0` | TCP | `80` | HTTP Web Traffic (Nginx) |
| `0.0.0.0/0` | TCP | `443` | HTTPS Encrypted Web Traffic |
| `0.0.0.0/0` | TCP | `3000` | Optional: Direct Frontend Access |

> [!CAUTION]
> **Do NOT expose Port 5431 (PostgreSQL) or Port 6379 (Redis)!**
> The application binds internal databases to `127.0.0.1`. Keeping them off the public internet prevents unauthorized brute-force attempts.

---

## 4. Step 3: Server Configuration & Host Firewall Setup

Connect via SSH to your Oracle Cloud VM:
```bash
ssh ubuntu@130.210.26.198
# (or ssh opc@130.210.26.198 for Oracle Linux)
```

Clone or pull the latest repository:
```bash
cd ~
git clone https://github.com/shubhamprakash681/ai-job-agent.git
# or if already cloned:
cd ai-job-agent
git pull origin main
```

Run the automated host setup script to configure Docker, ARM64 swap space, and host firewall:
```bash
sudo ./scripts/oci_setup.sh
```

### Manual Host Firewall Unblock (Ubuntu on OCI)
If you previously saw `Connection refused` on Port 80, ensure the host `iptables` allow rules are applied at the top of your INPUT chain:
```bash
sudo iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 3000 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
```

---

## 5. Step 4: Configure Production Environment (`.env`)

In your project directory (`~/ai-job-agent`):
```bash
cp .env.example .env
nano .env
```

Ensure the following variables are set specifically for **`agent.jobs.shubhamprakash681.in`**:

```ini
# Application Mode
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate_a_long_random_hex_string_using_openssl

# Database Credentials
POSTGRES_USER=jobagent
POSTGRES_PASSWORD=YourStrongDatabasePassword123!
POSTGRES_DB=jobagent
DATABASE_URL=postgresql+asyncpg://jobagent:YourStrongDatabasePassword123!@postgres:5432/jobagent

# Redis
REDIS_URL=redis://redis:6379/0

# Cloud Port & Security Bindings
FRONTEND_PORT=3000
POSTGRES_PORT_BINDING=127.0.0.1:5431
REDIS_PORT_BINDING=127.0.0.1:6379
BACKEND_PORT_BINDING=127.0.0.1:8000
PGADMIN_PORT_BINDING=127.0.0.1:5050

# CORS & Networking (Customized for your domain)
CORS_ORIGINS=["http://localhost:3000","http://agent.jobs.shubhamprakash681.in","https://agent.jobs.shubhamprakash681.in","http://130.210.26.198"]
BACKEND_API_URL=http://backend:8000
NEXT_PUBLIC_API_URL=http://agent.jobs.shubhamprakash681.in

# AI Providers (At least one enabled)
GROQ_API_KEY=gsk_...
GROQ_ENABLED=true
GEMINI_API_KEY=AIzaSy...
GEMINI_ENABLED=true
```

---

## 6. Step 5: Launch the Application with Nginx on Port 80

To serve the application on standard HTTP **Port 80** with Nginx:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Verify Listening Ports
Run:
```bash
sudo ss -tulpn | grep -wE ':(80|3000)'
```
Expected output:
```
tcp   LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("docker-proxy"...))
tcp   LISTEN 0      4096         0.0.0.0:3000       0.0.0.0:*    users:(("docker-proxy"...))
```

### Verify Local HTTP Response
```bash
curl -I http://localhost/
```
*(Should return `HTTP/1.1 200 OK` or `HTTP/1.1 307 Temporary Redirect` to `/dashboard`).*

Now, open your browser and navigate to:
👉 **`http://agent.jobs.shubhamprakash681.in/`**

---

## 7. Step 6: Setting Up Free HTTPS / SSL with Let's Encrypt

To enable secure `https://agent.jobs.shubhamprakash681.in/`:

1. Install Certbot on the VM:
   ```bash
   sudo apt-get install -y certbot  # On Ubuntu
   # or: sudo dnf install -y certbot # On Oracle Linux
   ```

2. Temporarily stop the containers to free Port 80 for the ACME challenge:
   ```bash
   docker compose down
   ```

3. Obtain the SSL Certificate:
   ```bash
   sudo certbot certonly --standalone -d agent.jobs.shubhamprakash681.in
   ```

4. Copy the issued certificate files into the Nginx SSL directory:
   ```bash
   sudo cp /etc/letsencrypt/live/agent.jobs.shubhamprakash681.in/fullchain.pem ./nginx/ssl/
   sudo cp /etc/letsencrypt/live/agent.jobs.shubhamprakash681.in/privkey.pem ./nginx/ssl/
   sudo chown -R $USER:$USER ./nginx/ssl/
   ```

5. Restart the containers with Nginx:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

Now access your site securely at:
👉 **`https://agent.jobs.shubhamprakash681.in/`**

---

## 8. Routine Operations & Maintenance

### Check Container Status
```bash
docker compose ps
```

### View Live Logs
```bash
docker compose logs -f frontend
docker compose logs -f backend
docker compose logs -f nginx
```

### Database Backup
```bash
./scripts/backup.sh
```
*(Creates a timestamped snapshot of PostgreSQL data in `./backups/`).*

### Access pgAdmin 4 via Secure SSH Tunnel
Since pgAdmin is securely restricted to localhost (`127.0.0.1:5050`):
```bash
ssh -L 5050:localhost:5050 -i ~/.ssh/id_rsa ubuntu@130.210.26.198
```
Then open `http://localhost:5050` on your local laptop browser.
