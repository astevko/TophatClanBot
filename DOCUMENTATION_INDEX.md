# Documentation Index

Complete guide to all documentation for the TophatC Clan Discord Bot.

## 📚 Quick Navigation

### 🚀 Getting Started
- **[README.md](README.md)** - Main project overview, features, and quick start
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup instructions for Discord and Roblox
- **[COMMANDS_GUIDE.md](COMMANDS_GUIDE.md)** - Complete command reference with examples

### ☁️ Deployment Guides

#### Oracle Cloud Infrastructure (OCI)
- **[OCI_DEPLOYMENT_GUIDE.md](OCI_DEPLOYMENT_GUIDE.md)** ⭐ - Complete OCI free tier deployment (recommended)
- **[QUICK_START_OCI.md](QUICK_START_OCI.md)** - Fast-track OCI deployment (30 minutes)
- **[OCI_NETWORK_REQUIREMENTS.md](OCI_NETWORK_REQUIREMENTS.md)** - Network ingress/egress requirements and security
- **[BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md)** - Database backup and migration to OCI

#### Docker Deployment
- **[README_DOCKER.md](README_DOCKER.md)** - Docker quick reference
- **[DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)** - Comprehensive Docker deployment guide
- **[DOCKER_CICD_SUMMARY.md](DOCKER_CICD_SUMMARY.md)** - CI/CD with Docker and GitHub Actions

#### Other Platforms
- **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** - Deploy to Railway.app free tier
- **[README.md#cloud-deployment](README.md#cloud-deployment)** - Render.com and other cloud options

### 💾 Database Management
- **[BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md)** - Complete backup and restore procedures
- **[ORACLE_DEPLOYMENT_GUIDE.md](ORACLE_DEPLOYMENT_GUIDE.md)** ⭐ NEW - Oracle Autonomous Database setup
- **Scripts:**
  - `backup_sqlite.sh` - Automated SQLite backup
  - `backup_postgres.sh` - Automated PostgreSQL backup
  - `migrate_to_postgres.py` - SQLite to PostgreSQL migration tool
  - `migrate_postgres_to_oracle.py` - PostgreSQL to Oracle migration tool
  - `test_oracle_connection.py` - Test Oracle database connectivity

### 🔧 Configuration & Customization
- **[RANK_CUSTOMIZATION.md](RANK_CUSTOMIZATION.md)** - Customize ranks and point requirements
- **[RANK_IDENTIFICATION_GUIDE.md](RANK_IDENTIFICATION_GUIDE.md)** - Find Roblox group rank IDs
- **[ADMIN_RANKS_GUIDE.md](ADMIN_RANKS_GUIDE.md)** - Configure admin-only ranks
- **[ROLE_PERMISSIONS_GUIDE.md](ROLE_PERMISSIONS_GUIDE.md)** - Discord role permissions setup

### 🔗 Roblox Integration
- **[ROBLOX_API_FIX.md](ROBLOX_API_FIX.md)** - Roblox API troubleshooting
- **[ROBLOX_SYNC_GUIDE.md](ROBLOX_SYNC_GUIDE.md)** - Rank synchronization with Roblox
- **[ROBLOX_PRIORITY_SYSTEM.md](ROBLOX_PRIORITY_SYSTEM.md)** - Roblox as source of truth for ranks
- **[PROMOTION_ROBLOX_UPDATE.md](PROMOTION_ROBLOX_UPDATE.md)** - Promotion system updates

### 🐛 Troubleshooting & Fixes
- **[RATE_LIMIT_FIXES.md](RATE_LIMIT_FIXES.md)** - Discord rate limit handling
- **[RATE_LIMIT_RETRY_UPDATE.md](RATE_LIMIT_RETRY_UPDATE.md)** - Rate limit retry logic
- **[SYNC_FIX_GUIDE.md](SYNC_FIX_GUIDE.md)** - Sync troubleshooting
- **[DISCORD_LOGGING_FIX.md](DISCORD_LOGGING_FIX.md)** - Logging configuration
- **[DISCORD_LOG_CONTROL.md](DISCORD_LOG_CONTROL.md)** - Log level control
- **[RESTART_REQUIRED.md](RESTART_REQUIRED.md)** - When to restart the bot

### 🔐 Security
- **[SECURITY.md](SECURITY.md)** - Security policy and reporting
- **[SECURITY_FIXES_APPLIED.md](SECURITY_FIXES_APPLIED.md)** - Security improvements log
- **[SECURITY_SCAN_REPORT.md](SECURITY_SCAN_REPORT.md)** - Security scan results
- **[SECURITY_SCAN_NOVEMBER_2025.md](SECURITY_SCAN_NOVEMBER_2025.md)** - Latest security scan

---

## 📖 Documentation by Use Case

### I want to run the bot locally for the first time
1. [README.md - Quick Start](README.md#quick-start)
2. [SETUP_GUIDE.md](SETUP_GUIDE.md)
3. [COMMANDS_GUIDE.md](COMMANDS_GUIDE.md)

### I want to deploy to Oracle Cloud (free forever)
1. [OCI_DEPLOYMENT_GUIDE.md](OCI_DEPLOYMENT_GUIDE.md) - Full instructions
2. [QUICK_START_OCI.md](QUICK_START_OCI.md) - Fast deployment
3. [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md) - Migrate your data

### I want to deploy with Docker
1. [README_DOCKER.md](README_DOCKER.md) - Quick reference
2. [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Full guide
3. [DOCKER_CICD_SUMMARY.md](DOCKER_CICD_SUMMARY.md) - Automation

### I want to backup my database
1. [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md) - Complete guide
2. Run `./backup_sqlite.sh` or `./backup_postgres.sh`

### I want to migrate from SQLite to PostgreSQL
1. [BACKUP_RESTORE_GUIDE.md#4-migrate-to-postgresql-on-oci](BACKUP_RESTORE_GUIDE.md#4-migrate-to-postgresql-on-oci)
2. Run `python migrate_to_postgres.py <database_url>`

### I want to migrate to Oracle Autonomous Database
1. [ORACLE_DEPLOYMENT_GUIDE.md](ORACLE_DEPLOYMENT_GUIDE.md) - Oracle setup guide
2. Run `python test_oracle_connection.py` - Test connection
3. Run `python migrate_postgres_to_oracle.py` - Migrate data

### I want to customize ranks
1. [RANK_CUSTOMIZATION.md](RANK_CUSTOMIZATION.md)
2. [RANK_IDENTIFICATION_GUIDE.md](RANK_IDENTIFICATION_GUIDE.md)
3. [ADMIN_RANKS_GUIDE.md](ADMIN_RANKS_GUIDE.md)

### I need to troubleshoot Roblox integration
1. [ROBLOX_API_FIX.md](ROBLOX_API_FIX.md)
2. [ROBLOX_SYNC_GUIDE.md](ROBLOX_SYNC_GUIDE.md)
3. [SYNC_FIX_GUIDE.md](SYNC_FIX_GUIDE.md)

### I'm getting rate limit errors
1. [RATE_LIMIT_FIXES.md](RATE_LIMIT_FIXES.md)
2. [RATE_LIMIT_RETRY_UPDATE.md](RATE_LIMIT_RETRY_UPDATE.md)

### I need help with commands
1. [COMMANDS_GUIDE.md](COMMANDS_GUIDE.md) - Full command reference
2. [README.md#commands](README.md#commands) - Quick reference

---

## 🛠️ Utility Scripts

Located in project root:

### Backup Scripts
- **`backup_sqlite.sh`** - Automated SQLite backup with compression and retention
- **`backup_postgres.sh`** - Automated PostgreSQL backup with compression and retention

### Migration Scripts
- **`migrate_to_postgres.py`** - Migrate data from SQLite to PostgreSQL
- **`migrate_postgres_to_oracle.py`** - Migrate data from PostgreSQL to Oracle
- **`migrate_add_admin_ranks.py`** - Add admin-only ranks to existing database

### Test Scripts
- **`test_oracle_connection.py`** - Test Oracle database connection and verify setup

### Run Scripts
- **`run.sh`** - Quick start for Linux/macOS
- **`run.bat`** - Quick start for Windows

### Setup Files
- **`setup_example.env`** - Environment variable template
- **`requirements.txt`** - Python dependencies
- **`pyproject.toml`** - Project metadata and uv configuration

---

## 📦 File Structure

```
TophatClanBot/
├── Documentation (Guides)
│   ├── OCI_DEPLOYMENT_GUIDE.md          # OCI deployment
│   ├── QUICK_START_OCI.md               # Fast OCI setup
│   ├── ORACLE_DEPLOYMENT_GUIDE.md       # Oracle database setup ⭐ NEW
│   ├── BACKUP_RESTORE_GUIDE.md          # Backup & migration
│   ├── README_DOCKER.md                 # Docker quick ref
│   ├── DOCKER_DEPLOYMENT.md             # Docker full guide
│   ├── COMMANDS_GUIDE.md                # Command reference
│   ├── SETUP_GUIDE.md                   # Setup instructions
│   └── [Other guides...]
│
├── Source Code
│   ├── bot.py                           # Main bot entry
│   ├── database.py                      # SQLite operations
│   ├── database_postgres.py             # PostgreSQL operations
│   ├── database_oracle.py               # Oracle operations ⭐ NEW
│   ├── roblox_api.py                    # Roblox integration
│   ├── config.py                        # Configuration
│   ├── security_utils.py                # Security utilities
│   └── commands/
│       ├── user_commands.py             # User commands
│       └── admin_commands.py            # Admin commands
│
├── Deployment
│   ├── Dockerfile                       # Production image
│   ├── docker-compose.yml               # Production stack
│   ├── docker-compose.dev.yml           # Development stack
│   ├── .dockerignore                    # Docker optimization
│   └── Makefile                         # Build automation
│
├── Scripts
│   ├── backup_sqlite.sh                 # SQLite backup
│   ├── backup_postgres.sh               # PostgreSQL backup
│   ├── migrate_to_postgres.py           # SQLite to PostgreSQL migration
│   ├── migrate_postgres_to_oracle.py    # PostgreSQL to Oracle migration ⭐ NEW
│   ├── test_oracle_connection.py        # Oracle connection test ⭐ NEW
│   ├── run.sh / run.bat                 # Quick start
│   └── migrate_add_admin_ranks.py       # Schema migration
│
└── Configuration
    ├── .env                             # Your config (not in git)
    ├── setup_example.env                # Template
    ├── requirements.txt                 # Dependencies
    ├── pyproject.toml                   # Project metadata
    └── .gitignore                       # Git ignore rules
```

---

## 🔍 Finding Information

### By Topic

| Topic | Documentation |
|-------|--------------|
| **Installation** | [README.md](README.md), [SETUP_GUIDE.md](SETUP_GUIDE.md) |
| **Commands** | [COMMANDS_GUIDE.md](COMMANDS_GUIDE.md) |
| **OCI Deployment** | [OCI_DEPLOYMENT_GUIDE.md](OCI_DEPLOYMENT_GUIDE.md), [QUICK_START_OCI.md](QUICK_START_OCI.md) |
| **Oracle Database** | [ORACLE_DEPLOYMENT_GUIDE.md](ORACLE_DEPLOYMENT_GUIDE.md) ⭐ NEW |
| **Network/Firewall** | [OCI_NETWORK_REQUIREMENTS.md](OCI_NETWORK_REQUIREMENTS.md) |
| **Docker** | [README_DOCKER.md](README_DOCKER.md), [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) |
| **Database** | [BACKUP_RESTORE_GUIDE.md](BACKUP_RESTORE_GUIDE.md), [ORACLE_DEPLOYMENT_GUIDE.md](ORACLE_DEPLOYMENT_GUIDE.md) |
| **Ranks** | [RANK_CUSTOMIZATION.md](RANK_CUSTOMIZATION.md), [ADMIN_RANKS_GUIDE.md](ADMIN_RANKS_GUIDE.md) |
| **Roblox** | [ROBLOX_API_FIX.md](ROBLOX_API_FIX.md), [ROBLOX_SYNC_GUIDE.md](ROBLOX_SYNC_GUIDE.md) |
| **Troubleshooting** | [RATE_LIMIT_FIXES.md](RATE_LIMIT_FIXES.md), [SYNC_FIX_GUIDE.md](SYNC_FIX_GUIDE.md) |
| **Security** | [SECURITY.md](SECURITY.md), [SECURITY_FIXES_APPLIED.md](SECURITY_FIXES_APPLIED.md) |

---

## 📝 Contributing to Documentation

When adding new documentation:

1. **Create the guide** in the project root
2. **Update this index** with a link to your guide
3. **Update README.md** if it's a major feature
4. **Follow naming conventions**:
   - Use UPPERCASE_WITH_UNDERSCORES.md for guides
   - Use descriptive names (e.g., `OCI_DEPLOYMENT_GUIDE.md`)
5. **Include**:
   - Table of contents for long guides
   - Clear step-by-step instructions
   - Code examples
   - Troubleshooting section

---

## 🆘 Getting Help

1. **Check relevant documentation** using this index
2. **Search existing issues** on GitHub
3. **Review logs** (`bot.log` or `docker compose logs`)
4. **Check Discord/Roblox API status**
5. **Open a GitHub issue** with:
   - Description of the problem
   - Steps to reproduce
   - Relevant logs (sanitized)
   - Environment details

---

## 📅 Last Updated

This index was last updated: November 15, 2025

For the most current information, always check the main [README.md](README.md).

---

**Happy Hosting! 🎉**

