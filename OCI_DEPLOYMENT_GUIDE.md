# Oracle Cloud Infrastructure (OCI) Free Tier Deployment Guide

This guide will walk you through deploying your TophatC Clan Discord Bot to Oracle Cloud Infrastructure's Always Free tier.

## Table of Contents
1. [OCI Account Setup](#1-oci-account-setup)
2. [Create a Compute Instance (VM)](#2-create-a-compute-instance-vm)
3. [Initial Server Setup](#3-initial-server-setup)
4. [Database Setup (PostgreSQL)](#4-database-setup-postgresql)
5. [Install Docker and Docker Compose](#5-install-docker-and-docker-compose)
6. [Deploy the Bot](#6-deploy-the-bot)
7. [Configure Firewall](#7-configure-firewall)
8. [Set Up Automatic Restarts](#8-set-up-automatic-restarts)
9. [Monitoring and Logs](#9-monitoring-and-logs)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. OCI Account Setup

### Create an OCI Account
1. Go to https://www.oracle.com/cloud/free/
2. Click "Start for free" and create an account
3. Complete identity verification (credit card required but won't be charged)
4. Choose your home region (this cannot be changed later, choose closest to your users)

### OCI Free Tier Resources
OCI Always Free tier includes:
- **2 AMD Compute VMs** (1/8 OCPU, 1 GB RAM each)
- **OR 4 Arm-based Ampere A1 cores** (24 GB RAM total) - **RECOMMENDED**
- **200 GB Block Storage**
- **10 GB Object Storage**
- **Autonomous Database** (2 OCPUs, 20 GB storage)

**Recommendation:** Use the Arm-based Ampere A1 instance for better performance.

---

## 2. Create a Compute Instance (VM)

### Step 1: Navigate to Compute Instances
1. Log in to OCI Console: https://cloud.oracle.com/
2. Open the navigation menu (☰)
3. Go to **Compute** → **Instances**
4. Click **Create Instance**

### Step 2: Configure the Instance
Fill in the following:

#### Basic Configuration
- **Name:** `tophat-bot-server`
- **Compartment:** (root) or create a new one

#### Placement
- **Availability Domain:** (Select any available)

#### Image and Shape
1. **Image:** 
   - Click "Change Image"
   - Select **Ubuntu 22.04 Minimal** (recommended) or **Oracle Linux 8**
   
2. **Shape:**
   - Click "Change Shape"
   - Select **Ampere (Arm-based)**
   - Choose **VM.Standard.A1.Flex**
   - **OCPUs:** 2 (or up to 4 if you want more power)
   - **Memory:** 12 GB (or up to 24 GB with 4 OCPUs)
   - This configuration is FREE under Always Free tier

#### Networking
- **Virtual Cloud Network (VCN):** Create new or select existing
- **Subnet:** Public subnet (default)
- **Assign a public IPv4 address:** ✅ **YES** (required)

#### SSH Keys
- **Add SSH keys:** 
  - Choose "Generate SSH key pair" and download both keys
  - **OR** paste your existing public SSH key
  - **Important:** Save the private key securely - you'll need it to connect

#### Boot Volume
- **Default** (50 GB is sufficient)

### Step 3: Create the Instance
1. Click **Create**
2. Wait 1-2 minutes for the instance to provision
3. Note the **Public IP address** once it's running

---

## 3. Initial Server Setup

### Connect to Your Instance

```bash
# SSH into your instance (replace with your IP and key path)
ssh -i /path/to/your-private-key ubuntu@YOUR_PUBLIC_IP

# If using Oracle Linux instead:
ssh -i /path/to/your-private-key oraclelinux@YOUR_PUBLIC_IP
```

### Update System Packages

```bash
# Update package lists and upgrade
sudo apt update && sudo apt upgrade -y

# Install essential tools
sudo apt install -y git curl wget vim htop
```

### Configure Firewall on the Instance

```bash
# Allow SSH (should already be open)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

---

## 4. Database Setup (PostgreSQL)

You have two options for PostgreSQL on OCI:

### Option A: Autonomous Database (Recommended - Managed Service)

#### Create Autonomous Database
1. In OCI Console, go to **Oracle Database** → **Autonomous Database**
2. Click **Create Autonomous Database**
3. Configure:
   - **Compartment:** (root)
   - **Display name:** `tophat-bot-db`
   - **Database name:** `tophatdb`
   - **Workload type:** Transaction Processing
   - **Deployment type:** Shared Infrastructure
   - **Database version:** 19c or 21c
   - **OCPU count:** 1 (Always Free)
   - **Storage:** 20 GB (Always Free)
   - **Auto scaling:** Disabled (for Always Free)
   - **Password:** Create a strong password (save it!)
   - **Network access:** Allow secure access from everywhere
4. Click **Create Autonomous Database**
5. Wait for provisioning (3-5 minutes)

#### Get Connection String
1. Click on your database name
2. Click **DB Connection**
3. Download the **Wallet** (credentials)
4. Note the connection strings - you'll need the **TLS** or **mTLS** connection string

**Note:** Autonomous Database requires wallet configuration. For simplicity, **Option B** is easier to set up.

---

### Option B: PostgreSQL on the VM (Simpler)

This is simpler and works well for small-to-medium bots.

```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE tophatclan;
CREATE USER botuser WITH ENCRYPTED PASSWORD 'YOUR_SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON DATABASE tophatclan TO botuser;
\c tophatclan
GRANT ALL ON SCHEMA public TO botuser;
EOF

# Edit PostgreSQL to allow local connections (Docker will connect via localhost)
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/*/main/postgresql.conf

# Allow connections from Docker network
echo "host    all             all             172.16.0.0/12            md5" | sudo tee -a /etc/postgresql/*/main/pg_hba.conf

# Restart PostgreSQL
sudo systemctl restart postgresql
```

Your PostgreSQL connection URL will be:
```
postgresql://botuser:YOUR_SECURE_PASSWORD_HERE@localhost:5432/tophatclan
```

---

## 5. Install Docker and Docker Compose

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group (avoid sudo)
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Log out and back in for group changes to take effect
exit
# SSH back in
ssh -i /path/to/your-private-key ubuntu@YOUR_PUBLIC_IP

# Verify installations
docker --version
docker compose version
```

---

## 6. Deploy the Bot

### Clone Your Repository

```bash
# Clone your bot repository
cd ~
git clone https://github.com/YOUR_USERNAME/TophatClanBot.git
cd TophatClanBot
```

### Create Environment File

```bash
# Create .env file with your configuration
cat > .env << 'EOF'
# PostgreSQL Configuration
POSTGRES_PASSWORD=YOUR_SECURE_DB_PASSWORD_HERE

# Database URL (if using PostgreSQL on VM)
# For Docker Compose, use 'postgres' as hostname
DATABASE_URL=postgresql://botuser:YOUR_SECURE_DB_PASSWORD_HERE@postgres:5432/tophatclan

# Discord Configuration
DISCORD_BOT_TOKEN=your_discord_bot_token_here
GUILD_ID=your_guild_id_here
LOG_CHANNEL_ID=your_log_channel_id_here
ADMIN_CHANNEL_ID=your_admin_channel_id_here

# Roblox Configuration
ROBLOX_GROUP_ID=your_roblox_group_id_here
ROBLOX_API_KEY=your_roblox_api_key_here
ROBLOX_COOKIE=your_roblox_cookie_here

# Role Configuration
ADMIN_ROLE_NAME=Admin
MODERATOR_ROLE_NAME=Moderator
OFFICER_ROLE_NAME=Officer
ELITE_ROLE_NAME=Elite
MEMBER_ROLE_NAME=Member

# Admin User IDs (comma-separated)
ADMIN_USER_IDS=123456789012345678,987654321098765432

# Rate Limiting
MAX_RATE_LIMIT_RETRIES=3
RATE_LIMIT_RETRY_DELAY=1.0
EOF

# Secure the .env file
chmod 600 .env
```

### Alternative: Use Standalone PostgreSQL (Outside Docker)

If you installed PostgreSQL directly on the VM (Option B above), modify your `.env`:

```bash
# Use 'host.docker.internal' or the VM's internal IP instead of 'postgres'
# Find your internal IP:
hostname -I | awk '{print $1}'

# In .env, use:
DATABASE_URL=postgresql://botuser:YOUR_SECURE_DB_PASSWORD_HERE@172.x.x.x:5432/tophatclan
```

And modify `docker-compose.yml` to remove the postgres service:

```yaml
version: '3.8'

services:
  # Discord Bot only (PostgreSQL is external)
  bot:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: tophat-bot
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./logs:/app/logs
    network_mode: "host"  # Use host network to access PostgreSQL on localhost
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Build and Start the Bot

```bash
# Build and start containers
docker compose up -d --build

# Check logs
docker compose logs -f bot

# Check if containers are running
docker compose ps
```

### Verify Bot is Running

```bash
# Check bot logs
docker compose logs bot

# You should see:
# - "Database initialized successfully"
# - "Bot is ready!"
# - Connection to Discord successful
```

---

## 7. Configure Firewall

### Network Requirements Summary

The Discord bot is **primarily outbound-only**:
- ✅ **Ingress (Incoming):** Only SSH (port 22) from your IP
- ✅ **Egress (Outgoing):** HTTPS (443) to Discord, Roblox, and package repos

📖 **See [OCI_NETWORK_REQUIREMENTS.md](OCI_NETWORK_REQUIREMENTS.md) for complete network documentation**

### OCI Security List Configuration

By default, OCI blocks all incoming traffic except SSH. Since your bot only makes outbound connections (to Discord and Roblox), you typically don't need to open any additional ports.

#### Recommended Configuration

1. In OCI Console, go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. **Ingress Rules** - Verify/Edit SSH rule:
   - **Source CIDR:** `YOUR_IP/32` (your home IP only - **never** use `0.0.0.0/0`)
   - **Destination Port:** `22`
   - **IP Protocol:** TCP
   - **Description:** SSH from my home IP

4. **Egress Rules** - Should already exist (default):
   - **Destination CIDR:** `0.0.0.0/0`
   - **IP Protocol:** All Protocols
   - **Description:** Allow all outbound traffic

**Find your IP:**
```bash
curl ifconfig.me
# Example output: 203.0.113.45
# Use in Security List: 203.0.113.45/32
```

#### Optional: Remote PostgreSQL Access (Not Recommended)

**⚠️ Better alternative: Use SSH tunnel instead**

```bash
# SSH tunnel (more secure)
ssh -i your-key.pem -L 5432:localhost:5432 ubuntu@YOUR_OCI_IP

# Then connect to localhost on your machine
psql -h localhost -U botuser -d tophatclan
```

If you must open PostgreSQL directly:
1. **Add Ingress Rule:**
   - **Source CIDR:** `YOUR_IP/32` (your home IP only for security)
   - **Destination Port:** `5432`
   - **IP Protocol:** TCP
   - **Description:** PostgreSQL from my home IP

**Warning:** Do NOT expose PostgreSQL to `0.0.0.0/0` (public internet) for security reasons.

### Instance Firewall (UFW)

```bash
# Check firewall status
sudo ufw status

# If you need to allow PostgreSQL from specific IP (optional)
sudo ufw allow from YOUR_HOME_IP to any port 5432
```

---

## 8. Set Up Automatic Restarts

Docker Compose is already configured with `restart: unless-stopped`, so containers will automatically restart on:
- Server reboot
- Container crash
- Manual stop (won't restart unless you `docker compose down`)

### Verify Restart Policy

```bash
docker inspect tophat-bot | grep -A 5 RestartPolicy
```

You should see:
```json
"RestartPolicy": {
    "Name": "unless-stopped",
    ...
}
```

### Enable Docker Service on Boot

```bash
sudo systemctl enable docker
```

---

## 9. Monitoring and Logs

### View Live Logs

```bash
# Follow bot logs
docker compose logs -f bot

# Follow all container logs
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100 bot
```

### Check Resource Usage

```bash
# Check CPU and memory usage
docker stats

# System resource monitoring
htop
```

### Log Rotation

Logs are automatically rotated by Docker (configured in docker-compose.yml):
- Max size per file: 10 MB
- Max files: 3
- Total max: ~30 MB

### Persistent Logs

Logs are stored in `./logs/` directory on the host:

```bash
# View logs directory
ls -lh logs/

# Check bot.log
tail -f logs/bot.log
```

---

## 10. Troubleshooting

### Bot Won't Start

```bash
# Check container logs
docker compose logs bot

# Check if container is running
docker compose ps

# Restart bot
docker compose restart bot

# Rebuild and restart
docker compose up -d --build --force-recreate
```

### Database Connection Issues

```bash
# Test PostgreSQL connection from host
psql -h localhost -U botuser -d tophatclan
# Enter password when prompted

# Check if PostgreSQL is running
sudo systemctl status postgresql

# View PostgreSQL logs
sudo journalctl -u postgresql -f
```

### Discord Connection Issues

1. Verify bot token in `.env` is correct
2. Check Discord Developer Portal - ensure bot is enabled
3. Verify intents are enabled (Message Content, Server Members, Presence)

### Check Container Health

```bash
# Inspect container
docker inspect tophat-bot

# Check Docker logs
sudo journalctl -u docker -f

# Restart Docker daemon
sudo systemctl restart docker
```

### Out of Memory

```bash
# Check memory usage
free -h

# Check Docker memory usage
docker stats

# If using Arm A1, consider increasing RAM (up to 24 GB free)
```

### Update Bot Code

```bash
# Pull latest changes
cd ~/TophatClanBot
git pull origin main

# Rebuild and restart
docker compose down
docker compose up -d --build

# Or without downtime (rolling update)
docker compose up -d --build --no-deps bot
```

### Reset Everything

```bash
# Stop and remove all containers
docker compose down

# Remove all volumes (WARNING: deletes database)
docker compose down -v

# Start fresh
docker compose up -d --build
```

---

## Useful Commands Reference

```bash
# Start bot
docker compose up -d

# Stop bot
docker compose down

# Restart bot
docker compose restart bot

# View logs
docker compose logs -f bot

# Rebuild bot
docker compose up -d --build

# Check status
docker compose ps

# Access bot shell
docker compose exec bot bash

# Access database (if using Docker PostgreSQL)
docker compose exec postgres psql -U botuser -d tophatclan

# Check resource usage
docker stats
```

---

## Security Best Practices

1. **Never commit .env files** to Git
2. **Use strong passwords** for database
3. **Limit SSH access** to your IP only in OCI Security List
4. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```
5. **Monitor logs** for suspicious activity
6. **Backup database regularly** (see BACKUP_RESTORE_GUIDE.md)
7. **Use non-root user** (already configured in Dockerfile)

---

## Cost Monitoring

Even though you're using Always Free tier:
1. Monitor your usage in OCI Console → **Billing & Cost Management**
2. Set up budget alerts
3. Ensure your resources stay within Always Free limits:
   - Compute: 1-4 Arm OCPUs (24 GB RAM total)
   - Block Storage: Up to 200 GB
   - Database: 2 OCPUs, 20 GB storage

---

## Next Steps

- ✅ Bot is deployed and running
- 📊 Set up monitoring and alerting
- 💾 Configure database backups (see [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md))
- 🔐 Harden security (SSH keys only, fail2ban, etc.)
- 📈 Monitor resource usage and scale if needed

---

## Getting Help

If you encounter issues:
1. Check logs: `docker compose logs -f`
2. Review troubleshooting section above
3. Check GitHub issues
4. OCI Documentation: https://docs.oracle.com/en-us/iaas/
5. Discord.py Documentation: https://discordpy.readthedocs.io/

---

**Congratulations! Your bot is now running on Oracle Cloud Infrastructure! 🎉**

