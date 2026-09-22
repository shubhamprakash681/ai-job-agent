# Oracle Cloud Infrastructure (OCI) Deployment Guide

This guide details how to deploy the **AI Job Agent** on an Oracle Cloud Infrastructure (OCI) **`VM.Standard.A1.Flex`** compute instance.

---

## 1. Why `VM.Standard.A1.Flex`?

Oracle Cloud's `VM.Standard.A1.Flex` is powered by **Ampere Altra (ARM64 / aarch64)** processors. Under Oracle Cloud's "Always Free" tier, eligible accounts receive:
- Up to **4 OCPUs** (ARM64 cores)
- Up to **24 GB of RAM**
- **200 GB** boot volume storage
- Generous monthly outbound bandwidth

This makes it an ideal, cost-effective host for the AI Job Agent (PostgreSQL + Redis + FastAPI Backend + Next.js Frontend + Nginx).

---

## 2. Step 1: Provision the VM in Oracle Cloud Console

1. Log into your **Oracle Cloud Console**.
2. Navigate to **Compute** &rarr; **Instances** &rarr; Click **Create instance**.
3. Configure the instance:
   - **Name**: `ai-job-agent-vm`
   - **Image**: **Ubuntu 24.04 / 22.04 Minimal (aarch64)** (or **Oracle Linux 9 (aarch64)**)
   - **Shape**: Click **Change Shape** &rarr; Select **Ampere** &rarr; **`VM.Standard.A1.Flex`**.
     - Set **OCPUs**: `2` to `4`
     - Set **Memory**: `12 GB` to `24 GB`
   - **Networking**: Select your default VCN and Public Subnet. Ensure **Assign a public IPv4 address** is checked.
   - **Add SSH keys**: Paste your public SSH key (`id_rsa.pub` or `id_ed25519.pub`).
4. Click **Create** and wait 1–2 minutes for the instance status to show **Running**. Note down the **Public IP Address**.

---

## 3. Step 2: Configure OCI Virtual Cloud Network (VCN) Ingress Rules

By default, Oracle Cloud VCN firewalls block all incoming ports except SSH (port 22). You must allow web traffic:

1. In the OCI Console, navigate to **Networking** &rarr; **Virtual Cloud Networks**.
2. Click your VCN &rarr; Click your **Public Subnet** &rarr; Click the **Default Security List**.
3. Under **Ingress Rules**, click **Add Ingress Rules**:

| Source CIDR | IP Protocol | Destination Port Range | Description |
| :--- | :--- | :--- | :--- |
| `0.0.0.0/0` | TCP | `80` | HTTP Web Traffic (Nginx) |
| `0.0.0.0/0` | TCP | `443` | HTTPS Encrypted Web Traffic |
| `0.0.0.0/0` | TCP | `3000` | Optional: Direct Frontend Access |

> [!CAUTION]
> **Do NOT expose Port 5431 (PostgreSQL) or Port 6379 (Redis) in the OCI Security List!**
> The AI Job Agent binds internal databases to `127.0.0.1` inside the VM. Exposing them to `0.0.0.0/0` would allow internet bots to attempt brute-forcing your database.

---

## 4. Step 3: Connect to your VM & Run Automated Setup

Connect via SSH:
```bash
# For Ubuntu:
ssh -i ~/.ssh/id_rsa ubuntu@<YOUR_OCI_PUBLIC_IP>

# For Oracle Linux:
ssh -i ~/.ssh/id_rsa opc@<YOUR_OCI_PUBLIC_IP>
```

Clone your project repository onto the VM:
```bash
git clone <YOUR_GIT_REPO_URL> ai-job-agent
cd ai-job-agent
```

Run the automated OCI setup script:
```bash
sudo ./scripts/oci_setup.sh
```

### What `oci_setup.sh` does automatically:
- Installs Docker Engine & the Docker Compose v2 plugin for ARM64 (`aarch64`).
- Configures 4GB swap space to guarantee smooth container builds.
- Automatically opens ports `80`, `443`, and `3000` in the host OS firewall (`iptables` / `firewalld` / `ufw`), bypassing default OCI rejection filters.
- Creates and enables a systemd unit (`ai-job-agent.service`) so your application automatically restarts if the VM reboots.

---

## 5. Step 4: Configure Production Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
nano .env
```

Set the required production values:
```ini
# Application Mode
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=generate_a_long_random_hex_string_using_openssl

# Database Credentials
POSTGRES_USER=jobagent
POSTGRES_PASSWORD=Use_A_Strong_Random_Password_Here
POSTGRES_DB=jobagent
DATABASE_URL=postgresql+asyncpg://jobagent:Use_A_Strong_Random_Password_Here@postgres:5432/jobagent

# Redis
REDIS_URL=redis://redis:6379/0

# Cloud Port & Security Bindings
FRONTEND_PORT=3000
POSTGRES_PORT_BINDING=127.0.0.1:5431
REDIS_PORT_BINDING=127.0.0.1:6379
BACKEND_PORT_BINDING=127.0.0.1:8000
PGADMIN_PORT_BINDING=127.0.0.1:5050

# CORS (Replace with your OCI Public IP or Domain)
CORS_ORIGINS=["http://<YOUR_OCI_PUBLIC_IP>:3000","http://<YOUR_OCI_PUBLIC_IP>"]

# AI Providers (At least one recommended)
GROQ_API_KEY=gsk_...
GROQ_ENABLED=true
GEMINI_API_KEY=AIzaSy...
GEMINI_ENABLED=true
```

---

## 6. Step 5: Launch the Application

### Option A: Standard Deployment (Port 3000)
To run directly on port 3000:
```bash
docker compose up -d --build
```
Access the application at: `http://<YOUR_OCI_PUBLIC_IP>:3000`

### Option B: Production Reverse Proxy (Port 80 / 443 with Nginx) — Recommended
To serve on standard web ports with high-performance Nginx reverse proxy and caching:
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```
Access the application at: `http://<YOUR_OCI_PUBLIC_IP>`

---

## 7. Step 6: Setting Up HTTPS / SSL with Let's Encrypt (Optional)

If you have a domain pointing to your OCI Public IP (e.g. `jobs.yourdomain.com`):

1. Update `CORS_ORIGINS` in `.env` to include `https://jobs.yourdomain.com`.
2. Install Certbot on the host:
   ```bash
   sudo apt-get install -y certbot  # On Ubuntu
   # or: sudo dnf install -y certbot # On Oracle Linux
   ```
3. Request a standalone certificate (temporarily stop Nginx):
   ```bash
   docker compose down
   sudo certbot certonly --standalone -d jobs.yourdomain.com
   ```
4. Copy or link certificates into `./nginx/ssl`:
   ```bash
   sudo cp /etc/letsencrypt/live/jobs.yourdomain.com/fullchain.pem ./nginx/ssl/
   sudo cp /etc/letsencrypt/live/jobs.yourdomain.com/privkey.pem ./nginx/ssl/
   sudo chown -R $USER:$USER ./nginx/ssl/
   ```
5. Restart with production compose:
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

---

## 8. Step 7: Routine Maintenance & Operations

### View Live Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Run Database Backup
```bash
./scripts/backup.sh
```
*(Backups are saved to `./backups/<timestamp>` with full SQL dump and candidate files).*

### Access pgAdmin 4 Safely
Because pgAdmin is securely bound to `127.0.0.1:5050`, connect using an SSH tunnel from your local laptop:
```bash
ssh -L 5050:localhost:5050 -i ~/.ssh/id_rsa ubuntu@<YOUR_OCI_PUBLIC_IP>
```
Then open `http://localhost:5050` in your local browser and log in with your `PGADMIN_EMAIL` and `PGADMIN_PASSWORD`.

### Automatic VM Reboot Protection
The `ai-job-agent.service` systemd service was enabled by `oci_setup.sh`. To verify its status:
```bash
sudo systemctl status ai-job-agent.service
```
Whenever the Oracle Cloud VM restarts (maintenance, reboot, power event), all containers will automatically spin back up into their desired state.

