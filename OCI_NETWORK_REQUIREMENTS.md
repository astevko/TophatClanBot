# OCI Network Requirements for TophatC Clan Bot

Network ingress (incoming) and egress (outgoing) requirements for running the Discord bot on Oracle Cloud Infrastructure.

## Summary

**The bot is primarily outbound-only** - it connects to Discord and Roblox APIs, doesn't listen on any ports except SSH for management.

---

## 🔽 Ingress (Incoming Traffic)

### Required

| Port | Protocol | Source | Purpose | Required |
|------|----------|--------|---------|----------|
| 22 | TCP | Your IP | SSH server management | ✅ **Required** |

### Optional (Not Recommended)

| Port | Protocol | Source | Purpose | Security Risk |
|------|----------|--------|---------|---------------|
| 5432 | TCP | Your IP | Remote PostgreSQL access | ⚠️ **High** - Only if absolutely needed for remote database management |

### Recommendation

**Only open port 22 (SSH)** and restrict it to your IP address:
- ✅ SSH from your home/office IP only
- ❌ **Never** open to `0.0.0.0/0` (public internet)
- ❌ **Never** expose PostgreSQL to public internet
- ❌ Bot doesn't need any incoming ports (it initiates all connections)

---

## 🔼 Egress (Outgoing Traffic)

### Required Destinations

The bot needs to reach these external services:

| Destination | Port | Protocol | Purpose | Frequency |
|-------------|------|----------|---------|-----------|
| Discord API (`discord.com`, `discordapp.com`) | 443 | HTTPS | Bot communication with Discord | Constant |
| Discord Gateway (`gateway.discord.gg`) | 443 | WSS (WebSocket over TLS) | Real-time Discord events | Constant |
| Discord CDN (`cdn.discordapp.com`) | 443 | HTTPS | Image uploads/downloads | As needed |
| Roblox API (`*.roblox.com`) | 443 | HTTPS | Rank sync, user info | Frequent |
| Package Repos (`*.ubuntu.com`, `security.ubuntu.com`) | 80, 443 | HTTP/HTTPS | System updates | Manual |
| Docker Hub (`registry-1.docker.io`, `*.docker.io`) | 443 | HTTPS | Docker image pulls | Manual |
| GitHub (`github.com`, `raw.githubusercontent.com`) | 443 | HTTPS | Git clone, updates | Manual |
| PyPI (`pypi.org`, `files.pythonhosted.org`) | 443 | HTTPS | Python packages | Manual |

### Specific Endpoints

#### Discord (Required - Constant)
```
discord.com:443          (HTTPS) - API endpoints
discordapp.com:443       (HTTPS) - API endpoints  
gateway.discord.gg:443   (WSS)   - WebSocket gateway
cdn.discordapp.com:443   (HTTPS) - Content delivery
```

#### Roblox (Required - Frequent)
```
users.roblox.com:443     (HTTPS) - User info API
groups.roblox.com:443    (HTTPS) - Group management
apis.roblox.com:443      (HTTPS) - Open Cloud API
www.roblox.com:443       (HTTPS) - Web endpoints
```

#### System Updates (Optional - Manual)
```
archive.ubuntu.com:80,443
security.ubuntu.com:80,443
ports.ubuntu.com:80,443
```

#### Docker (Optional - Manual)
```
registry-1.docker.io:443
auth.docker.io:443
production.cloudflare.docker.com:443
```

---

## 📋 OCI Security List Configuration

### Default Configuration (Recommended)

OCI instances come with a default security list that:
- ✅ **Allows** all outbound traffic (egress)
- ❌ **Blocks** all inbound traffic except SSH (ingress)

**This is perfect for the Discord bot!** No changes needed to egress rules.

### Step-by-Step: Secure Your Instance

#### 1. Configure SSH Ingress (Required)

1. In OCI Console, go to **Networking** → **Virtual Cloud Networks**
2. Click your VCN → **Security Lists** → **Default Security List**
3. **Ingress Rules** → Find SSH rule (port 22)
4. **Edit the rule:**
   - **Source Type:** CIDR
   - **Source CIDR:** `YOUR_HOME_IP/32` (replace with your actual IP)
   - **IP Protocol:** TCP
   - **Destination Port Range:** 22
   - **Description:** SSH from my home/office

**Find your IP:**
```bash
curl ifconfig.me
# Example output: 203.0.113.45
# Use: 203.0.113.45/32
```

#### 2. Verify Egress Rules

1. **Egress Rules** section
2. Verify this rule exists (usually default):
   - **Destination Type:** CIDR
   - **Destination CIDR:** `0.0.0.0/0`
   - **IP Protocol:** All Protocols
   - **Description:** Allow all outbound traffic

**This allows the bot to reach Discord, Roblox, and all required services.**

#### 3. Optional: PostgreSQL Remote Access (Not Recommended)

**⚠️ Only if you need remote database access (use SSH tunnel instead)**

If you must open PostgreSQL:
1. **Add Ingress Rule:**
   - **Source Type:** CIDR
   - **Source CIDR:** `YOUR_HOME_IP/32` (your IP only!)
   - **IP Protocol:** TCP
   - **Destination Port Range:** 5432
   - **Description:** PostgreSQL from my home IP

**Better alternative: SSH tunnel**
```bash
# Create SSH tunnel (more secure)
ssh -i your-key.pem -L 5432:localhost:5432 ubuntu@YOUR_OCI_IP

# Now connect to localhost:5432 on your machine
psql -h localhost -U botuser -d tophatclan
```

---

## 🔒 Instance Firewall (UFW) Configuration

In addition to OCI Security Lists, configure UFW on the instance:

```bash
# Check UFW status
sudo ufw status

# Should see something like:
# Status: active
# 
# To                         Action      From
# --                         ------      ----
# 22/tcp                     ALLOW       YOUR_IP

# If UFW is not enabled
sudo ufw enable

# Allow SSH from your IP only
sudo ufw allow from YOUR_HOME_IP to any port 22

# Block all other incoming
sudo ufw default deny incoming

# Allow all outgoing (required for bot)
sudo ufw default allow outgoing
```

---

## 🧪 Testing Connectivity

### Test Outbound Connectivity

From your OCI instance:

```bash
# Test Discord API
curl -I https://discord.com/api/v10/gateway

# Expected: HTTP/2 200

# Test Roblox API
curl -I https://users.roblox.com/v1/users/1

# Expected: HTTP/2 200

# Test DNS resolution
nslookup discord.com
nslookup roblox.com

# Test WebSocket (Discord Gateway)
curl -I https://gateway.discord.gg

# Expected: HTTP/2 426 (upgrade required - normal for WebSocket)
```

### Test Inbound SSH

From your local machine:

```bash
# Test SSH connection
ssh -i your-key.pem ubuntu@YOUR_OCI_IP

# If it works, you're good!
# If timeout, check OCI Security List allows your IP
```

---

## 🌐 Network Architecture Diagram

```
┌─────────────────────────────────────────────┐
│           Your Home/Office Network          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │      Your Computer                    │  │
│  │  - SSH Client (port 22)               │  │
│  │  - psql Client (port 5432, optional)  │  │
│  └───────────────┬──────────────────────┘  │
│                  │                          │
└──────────────────┼──────────────────────────┘
                   │ INGRESS (SSH only)
                   │ Source: YOUR_IP/32
                   ▼
┌─────────────────────────────────────────────┐
│        Oracle Cloud Infrastructure          │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │    OCI Compute Instance (Ubuntu)      │  │
│  │                                        │  │
│  │  ┌──────────────────────────────────┐ │  │
│  │  │  Docker Container (Bot)           │ │  │
│  │  │  - Discord.py                     │ │  │
│  │  │  - Makes outbound connections     │ │  │
│  │  └──────────────────────────────────┘ │  │
│  │                                        │  │
│  │  ┌──────────────────────────────────┐ │  │
│  │  │  PostgreSQL Database              │ │  │
│  │  │  - Local only (no ingress)        │ │  │
│  │  └──────────────────────────────────┘ │  │
│  └────────────┬───────────────────────────┘  │
│               │                              │
└───────────────┼──────────────────────────────┘
                │ EGRESS (all allowed)
                │ Destination: 0.0.0.0/0
                ▼
┌─────────────────────────────────────────────┐
│          External Services (HTTPS/443)      │
│                                             │
│  • discord.com - Discord API                │
│  • gateway.discord.gg - Discord Gateway     │
│  • *.roblox.com - Roblox APIs               │
│  • docker.io - Docker images                │
│  • github.com - Git repositories            │
│  • pypi.org - Python packages               │
│  • *.ubuntu.com - System updates            │
└─────────────────────────────────────────────┘
```

---

## 📊 Bandwidth & Data Transfer

### Estimated Usage

| Activity | Bandwidth | Frequency |
|----------|-----------|-----------|
| Discord Gateway (idle) | ~5-10 KB/s | Constant |
| Discord Gateway (active) | ~20-50 KB/s | Variable |
| Command responses | ~2-5 KB per command | As needed |
| Image uploads (raids) | ~100-500 KB per image | Daily |
| Roblox API calls | ~1-2 KB per call | Hourly |
| Bot updates | ~50-100 MB | Monthly |
| System updates | ~50-200 MB | Monthly |

### OCI Free Tier Limits
- **Network bandwidth:** 10 TB/month egress (FREE)
- **Expected bot usage:** ~5-10 GB/month
- **Safety margin:** 99% under limit ✅

---

## 🔐 Security Best Practices

### ✅ Do's

1. **Restrict SSH to your IP:**
   ```bash
   # OCI Security List
   Source: YOUR_IP/32 (not 0.0.0.0/0)
   ```

2. **Use SSH keys (never passwords):**
   ```bash
   # Disable password auth
   sudo sed -i 's/PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
   sudo systemctl restart sshd
   ```

3. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

4. **Use SSH tunnels for database:**
   ```bash
   ssh -L 5432:localhost:5432 ubuntu@OCI_IP
   ```

5. **Monitor logs:**
   ```bash
   docker compose logs -f
   tail -f /var/log/auth.log  # SSH attempts
   ```

### ❌ Don'ts

1. ❌ **Never** open SSH to `0.0.0.0/0` (entire internet)
2. ❌ **Never** expose PostgreSQL to public internet
3. ❌ **Never** use weak SSH passwords (use keys!)
4. ❌ **Never** run bot as root (Docker handles this)
5. ❌ **Never** commit `.env` files with credentials

---

## 🛠️ Troubleshooting Network Issues

### Bot can't connect to Discord

```bash
# Check DNS resolution
nslookup discord.com

# Check HTTPS connectivity
curl -I https://discord.com/api/v10/gateway

# Check if OCI blocks egress (should not on free tier)
sudo iptables -L OUTPUT -n -v

# Check Docker network
docker network inspect tophatclanbot_botnet
```

### Bot can't connect to Roblox

```bash
# Check Roblox API
curl -I https://users.roblox.com/v1/users/1

# Check if Roblox is down
curl https://status.roblox.com/

# Verify API credentials in .env
```

### Can't SSH to instance

```bash
# Check your public IP changed
curl ifconfig.me

# Update OCI Security List with new IP

# Check instance is running
# OCI Console → Compute → Instances → Check status
```

### High bandwidth usage

```bash
# Monitor network usage
sudo apt install vnstat
vnstat -l  # Live traffic

# Check Docker container stats
docker stats

# Review bot logs for errors causing retries
docker compose logs --tail=100 bot | grep -i error
```

---

## 📝 Quick Reference

### Minimal Required Configuration

**OCI Security List:**
```yaml
Ingress:
  - Source: YOUR_IP/32
    Protocol: TCP
    Port: 22
    Description: SSH from home

Egress:
  - Destination: 0.0.0.0/0
    Protocol: All
    Description: Allow all outbound
```

**Instance Firewall (UFW):**
```bash
sudo ufw allow from YOUR_IP to any port 22
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw enable
```

**Required External Services:**
- `discord.com:443` - Discord API
- `gateway.discord.gg:443` - Discord Gateway
- `*.roblox.com:443` - Roblox APIs

---

## 📖 Related Documentation

- **[OCI_DEPLOYMENT_GUIDE.md](OCI_DEPLOYMENT_GUIDE.md)** - Complete deployment instructions
- **[QUICK_START_OCI.md](QUICK_START_OCI.md)** - Fast deployment guide
- **[SECURITY.md](SECURITY.md)** - Security best practices

---

**Last Updated:** November 15, 2025

