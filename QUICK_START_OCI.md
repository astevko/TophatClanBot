# Quick Start: Deploy to Oracle Cloud Infrastructure

Quick reference guide for deploying TophatC Clan Bot to OCI Free Tier.

## Prerequisites
- Oracle Cloud account (free tier)
- SSH key pair
- Discord bot token
- Roblox API credentials
- Local database to migrate (optional)

---

## 🚀 Fast Track Deployment (30 minutes)

### Step 1: Create OCI Instance (5 min)
1. Login to https://cloud.oracle.com/
2. Create Compute Instance:
   - **Shape:** VM.Standard.A1.Flex (Arm)
   - **OCPUs:** 2-4 (FREE)
   - **Memory:** 12-24 GB (FREE)
   - **Image:** Ubuntu 22.04
   - **Public IP:** YES
3. Download SSH key
4. Note public IP address

### Step 2: Connect & Setup Server (5 min)
```bash
# SSH to instance
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install -y docker-compose-plugin

# Log out and back in
exit
ssh -i your-key.pem ubuntu@YOUR_PUBLIC_IP
```

### Step 3: Setup PostgreSQL (5 min)
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database
sudo -u postgres psql << EOF
CREATE DATABASE tophatclan;
CREATE USER botuser WITH ENCRYPTED PASSWORD 'YOUR_STRONG_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE tophatclan TO botuser;
\c tophatclan
GRANT ALL ON SCHEMA public TO botuser;
EOF

# Enable PostgreSQL
sudo systemctl enable postgresql
```

### Step 4: Deploy Bot (10 min)
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/TophatClanBot.git
cd TophatClanBot

# Create .env file
cat > .env << 'EOF'
# Database
POSTGRES_PASSWORD=YOUR_STRONG_PASSWORD
DATABASE_URL=postgresql://botuser:YOUR_STRONG_PASSWORD@postgres:5432/tophatclan

# Discord
DISCORD_BOT_TOKEN=your_token_here
GUILD_ID=your_guild_id
LOG_CHANNEL_ID=your_log_channel_id
ADMIN_CHANNEL_ID=your_admin_channel_id

# Roblox
ROBLOX_GROUP_ID=your_group_id
ROBLOX_API_KEY=your_api_key
ROBLOX_COOKIE=your_cookie

# Roles
ADMIN_ROLE_NAME=Admin
ADMIN_USER_IDS=your_discord_id

# Rate Limiting
MAX_RATE_LIMIT_RETRIES=3
RATE_LIMIT_RETRY_DELAY=1.0
EOF

# Secure .env
chmod 600 .env

# Start bot
docker compose up -d --build

# Check logs
docker compose logs -f bot
```

### Step 5: Migrate Data (5 min, optional)
If you have existing data, see [Backup & Restore Guide](BACKUP_RESTORE_GUIDE.md#4-migrate-to-postgresql-on-oci)

---

## 📋 Useful Commands

### Bot Management
```bash
# Start bot
docker compose up -d

# Stop bot
docker compose down

# Restart bot
docker compose restart bot

# View logs
docker compose logs -f bot

# Update bot
git pull
docker compose up -d --build

# Check status
docker compose ps
docker stats
```

### Database Management
```bash
# Access database
docker compose exec postgres psql -U botuser -d tophatclan

# Backup database
pg_dump -h localhost -U botuser tophatclan | gzip > backup_$(date +%Y%m%d).sql.gz

# Restore database
gunzip -c backup.sql.gz | psql -h localhost -U botuser -d tophatclan

# Check database size
psql -h localhost -U botuser -d tophatclan -c "\l+"
```

### System Monitoring
```bash
# Check resources
htop
docker stats

# Check disk space
df -h

# Check logs
docker compose logs --tail=100 bot
tail -f logs/bot.log
```

---

## 🔧 Troubleshooting

### Bot Won't Start
```bash
# Check logs for errors
docker compose logs bot

# Verify environment variables
cat .env

# Rebuild
docker compose down
docker compose up -d --build
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U botuser -d tophatclan

# Check Docker network
docker network ls
docker network inspect tophatclanbot_botnet
```

### Out of Memory
```bash
# Check memory
free -h

# Restart Docker
sudo systemctl restart docker
docker compose restart
```

---

## 📚 Full Documentation

- **[OCI Deployment Guide](OCI_DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[Backup & Restore Guide](BACKUP_RESTORE_GUIDE.md)** - Database backup and migration
- **[Docker Deployment Guide](DOCKER_DEPLOYMENT.md)** - Docker-specific information
- **[Commands Guide](COMMANDS_GUIDE.md)** - Bot commands reference

---

## 🔐 Security Checklist

- ✅ Strong database password
- ✅ `.env` file secured (chmod 600)
- ✅ SSH key authentication only
- ✅ Firewall configured (UFW)
- ✅ Regular backups enabled
- ✅ Bot token kept secret
- ✅ OCI security lists configured

---

## 💰 Cost Monitoring

Your OCI Free Tier includes:
- ✅ **Compute:** 4 Arm OCPUs, 24 GB RAM (FREE forever)
- ✅ **Storage:** 200 GB (FREE forever)
- ✅ **Database:** 2 OCPUs, 20 GB (FREE forever)
- ✅ **Network:** 10 TB/month egress (FREE)

**Monitor usage:** OCI Console → Billing & Cost Management

---

## 🆘 Getting Help

1. Check logs: `docker compose logs -f`
2. Review [OCI Deployment Guide](OCI_DEPLOYMENT_GUIDE.md)
3. Check [Troubleshooting section](OCI_DEPLOYMENT_GUIDE.md#10-troubleshooting)
4. Review Discord.py docs: https://discordpy.readthedocs.io/
5. Check OCI docs: https://docs.oracle.com/en-us/iaas/

---

## 📞 Support

- GitHub Issues: https://github.com/YOUR_USERNAME/TophatClanBot/issues
- Documentation: All `.md` files in project root

---

**Happy Hosting! 🎉**

