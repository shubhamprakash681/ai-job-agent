# Oracle Cloud Infrastructure (OCI) Deployment Guide
## Production Target: Full HTTPS (Frontend: 3000, Backend: 4000)
### `https://agent.jobs.shubhamprakash681.in:3000` & `https://agent.jobs.shubhamprakash681.in:4000`

This guide details how to deploy and configure the **AI Job Agent** strictly over **HTTPS** on an Oracle Cloud Infrastructure (OCI) **`VM.Standard.A1.Flex`** compute instance (Ampere Altra ARM64) mapped to your domain **`agent.jobs.shubhamprakash681.in`**.

---

## 1. Architecture & Port Mapping (HTTPS Only)

- **Compute Instance**: Oracle Cloud `VM.Standard.A1.Flex` (Ampere Altra ARM64 / aarch64)
- **Public IP Address**: `130.210.26.198`
- **Domain Name**: `agent.jobs.shubhamprakash681.in`
- **DNS Provider**: GoDaddy (`domaincontrol.com`)
- **Port Mapping**:
  - **`3000` (HTTPS)**: Next.js Frontend Console &rarr; `https://agent.jobs.shubhamprakash681.in:3000`
  - **`4000` (HTTPS)**: FastAPI Backend API &rarr; `https://agent.jobs.shubhamprakash681.in:4000`
  - **`443` (HTTPS)**: Standard HTTPS (aliases frontend & API) &rarr; `https://agent.jobs.shubhamprakash681.in`
  - **`80` (HTTP)**: Automatically redirects all plain HTTP traffic to HTTPS (`301 Moved Permanently`)
  - **`5431` (PostgreSQL) & `6379` (Redis)**: Strictly bound to `127.0.0.1` (never exposed to public internet)

---

## 2. Step 1: DNS Configuration (GoDaddy)

Ensure the DNS record for your subdomain is active:

1. Log into your **GoDaddy DNS Management Console** for `shubhamprakash681.in`.
2. Verify or add the following **A Record**:

| Type | Name / Host | Value / Target | TTL |
| :--- | :--- | :--- | :--- |
| **A** | `agent.jobs` | `130.210.26.198` | 1/2 Hour (or 600s) |

> [!NOTE]
> Ensure the record name is **`agent.jobs`** (singular), which resolves to `agent.jobs.shubhamprakash681.in`.

---

## 3. Step 2: OCI Virtual Cloud Network (VCN) Ingress Rules

In your Oracle Cloud Console, ensure your VCN Security List allows web traffic on ports 80, 443, 3000, and 4000:

1. Go to **Networking** &rarr; **Virtual Cloud Networks** &rarr; Click your VCN.
2. Under Resources, click **Security Lists** &rarr; Select your **Default Security List for...**.
3. Under **Ingress Rules**, click **Add Ingress Rules** and ensure these 4 rules are present:

| Source CIDR | IP Protocol | Destination Port Range | Description |
| :--- | :--- | :--- | :--- |
| `0.0.0.0/0` | TCP | `80` | HTTP Web Traffic (Auto-redirect to HTTPS) |
| `0.0.0.0/0` | TCP | `443` | Standard HTTPS Encrypted Web Traffic |
| `0.0.0.0/0` | TCP | `3000` | HTTPS Frontend Application |
| `0.0.0.0/0` | TCP | `4000` | HTTPS Backend API Service |

> [!CAUTION]
> **Do NOT expose Port 5431 (PostgreSQL) or Port 6379 (Redis)!**
> The application binds internal databases to `127.0.0.1`. Keeping them off the public internet prevents unauthorized bot scans and brute-force attacks.

---

## 4. Step 3: Server Configuration & Host Firewall Setup

Connect via SSH to your Oracle Cloud VM:
```bash
ssh ubuntu@130.210.26.198
# (or ssh opc@130.210.26.198 for Oracle Linux)
```

Pull the latest repository updates:
```bash
cd ~/ai-job-agent
git pull origin main
```

Run the automated host setup script to configure Docker, ARM64 swap space, and host firewall rules:
```bash
sudo ./scripts/oci_setup.sh
```

### Manual Host Firewall Unblock (Ubuntu on OCI)
To guarantee that the host OS `iptables` permits incoming traffic on ports 80, 443, 3000, and 4000:
```bash
sudo iptables -I INPUT 1 -p tcp --dport 80 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 443 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 3000 -j ACCEPT
sudo iptables -I INPUT 1 -p tcp --dport 4000 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || sudo iptables-save | sudo tee /etc/iptables/rules.v4 > /dev/null
```

---

## 5. Step 4: Configure Production Environment (`.env`)

In your project directory (`~/ai-job-agent`):
```bash
nano .env
```

Ensure the following configuration is active for **HTTPS with Frontend (3000) and Backend (4000)**:

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
BACKEND_PORT_BINDING=127.0.0.1:4000
FRONTEND_PORT_BINDING=127.0.0.1:3001
POSTGRES_PORT_BINDING=127.0.0.1:5431
REDIS_PORT_BINDING=127.0.0.1:6379
PGADMIN_PORT_BINDING=127.0.0.1:5050

# CORS & Networking (HTTPS origins)
CORS_ORIGINS=["http://localhost:3000","https://localhost:3000","https://agent.jobs.shubhamprakash681.in:3000","https://agent.jobs.shubhamprakash681.in","https://agent.jobs.shubhamprakash681.in:4000"]
BACKEND_API_URL=http://backend:4000
NEXT_PUBLIC_API_URL=https://agent.jobs.shubhamprakash681.in:4000

# AI Providers
GROQ_API_KEY=gsk_...
GROQ_ENABLED=true
GEMINI_API_KEY=AIzaSy...
GEMINI_ENABLED=true
```

---

## 6. Step 5: Launch with HTTPS (Ports 3000 & 4000)

Pre-generated SSL certificates for `agent.jobs.shubhamprakash681.in` are committed in `./nginx/ssl/` so Nginx launches with full HTTPS immediately without error.

Run:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### Verify Listening Ports
Run:
```bash
sudo ss -tulpn | grep -wE ':(80|443|3000|4000)'
```
Expected output:
```
tcp   LISTEN 0      511          0.0.0.0:80         0.0.0.0:*    users:(("docker-proxy"...))
tcp   LISTEN 0      511          0.0.0.0:443        0.0.0.0:*    users:(("docker-proxy"...))
tcp   LISTEN 0      511          0.0.0.0:3000       0.0.0.0:*    users:(("docker-proxy"...))
tcp   LISTEN 0      511          0.0.0.0:4000       0.0.0.0:*    users:(("docker-proxy"...))
```

### Accessing the Platform
- **Frontend Console (HTTPS)**:
  👉 **`https://agent.jobs.shubhamprakash681.in:3000/`** *(or `https://agent.jobs.shubhamprakash681.in/`)*
- **Backend API (HTTPS)**:
  👉 **`https://agent.jobs.shubhamprakash681.in:4000/api/health`**
- **Plain HTTP requests (`http://...`)**:
  Automatically redirected to **HTTPS**.

---

## 7. Step 6: Upgrading to Official Let's Encrypt CA Certificates

The system boots with pre-configured SSL certificates. To upgrade to a browser-trusted CA certificate from Let's Encrypt:

1. Install Certbot on the VM:
   ```bash
   sudo apt-get install -y certbot  # On Ubuntu
   ```

2. Temporarily stop Nginx to free port 80:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml down
   ```

3. Obtain the certificate:
   ```bash
   sudo certbot certonly --standalone -d agent.jobs.shubhamprakash681.in
   ```

4. Copy the official certs into `./nginx/ssl`:
   ```bash
   sudo cp /etc/letsencrypt/live/agent.jobs.shubhamprakash681.in/fullchain.pem ./nginx/ssl/
   sudo cp /etc/letsencrypt/live/agent.jobs.shubhamprakash681.in/privkey.pem ./nginx/ssl/
   sudo chown -R $USER:$USER ./nginx/ssl/
   ```

5. Restart the containers:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

---

## 8. Routine Operations & Maintenance

### Check Container Status
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
```

### View Live Logs
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f nginx
docker compose logs -f frontend
docker compose logs -f backend
```

### Database Backup
```bash
./scripts/backup.sh
```

### Access pgAdmin 4 Safely (SSH Tunnel)
```bash
ssh -L 5050:localhost:5050 -i ~/.ssh/id_rsa ubuntu@130.210.26.198
```
Then open `http://localhost:5050` in your local browser.

---

## 9. Troubleshooting & Database Connection Fixes

### If Frontend shows "Failed to connect to the server" or `/api/health` reports `"db_status":"error"`:

This occurs when the backend container cannot authenticate or connect to PostgreSQL (e.g. password mismatch or unescaped characters in the database URL).

#### Step 1: Pull latest updates & rebuild backend
```bash
cd ~/ai-job-agent
git pull origin main
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build backend nginx
```

#### Step 2: Synchronize PostgreSQL password
If `postgres_data` volume was initialized previously with a different password, Postgres retains the original password. Synchronize it with your `.env` value:
```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "ALTER USER $POSTGRES_USER WITH PASSWORD '\''$POSTGRES_PASSWORD'\'';"'
```

#### Step 3: Run Database Schema Initialization & Seeding
```bash
docker compose exec backend python -c "import asyncio; from app.db.session import init_db; from app.db.init_db import init_db as seed_db; asyncio.run(init_db()); asyncio.run(seed_db())"
```

#### Step 4: Restart backend and verify
```bash
docker compose restart backend
curl -k https://agent.jobs.shubhamprakash681.in:4000/api/health
```
You should see:
`{"status":"ok","db_status":"ok",...}`

Now reload `https://agent.jobs.shubhamprakash681.in` or `https://agent.jobs.shubhamprakash681.in:3000` in your browser. The setup/login screen will load immediately!
