# Oracle Database Deployment Guide

This guide covers deploying the TophatC Clan Bot with Oracle Autonomous Database (ADB) on Oracle Cloud Infrastructure (OCI).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Database Setup](#database-setup)
3. [Configuration](#configuration)
4. [Wallet Authentication](#wallet-authentication)
5. [Deployment Options](#deployment-options)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Python Requirements

- Python 3.8 or higher
- For Python 3.13+: Additional wallet configuration options available

### Oracle Cloud Infrastructure

- OCI Account with access to Oracle Autonomous Database
- Oracle Autonomous Database (ATP or ADW) instance created

### Required Packages

The bot automatically installs the required Oracle driver:

```bash
pip install -r requirements.txt
```

This includes:
- `oracledb>=2.0.0` - Oracle Database driver for Python

## Database Setup

### 1. Create Oracle Autonomous Database

1. Log in to Oracle Cloud Console
2. Navigate to **Oracle Database** > **Autonomous Database**
3. Click **Create Autonomous Database**
4. Configure:
   - **Workload Type**: Transaction Processing (ATP) recommended
   - **Deployment Type**: Shared Infrastructure (free tier available)
   - **Database Name**: Choose a unique name (e.g., `TophatClanDB`)
   - **Display Name**: User-friendly name
   - **Admin Password**: Strong password for ADMIN user

### 2. Create Application User (Recommended)

Instead of using the ADMIN user, create a dedicated user:

```sql
-- Connect as ADMIN user
CREATE USER tophat_bot IDENTIFIED BY "YourSecurePassword123!";
GRANT CONNECT, RESOURCE TO tophat_bot;
GRANT UNLIMITED TABLESPACE TO tophat_bot;
```

### 3. Get Connection Details

1. In OCI Console, go to your Autonomous Database details
2. Click **DB Connection**
3. Select connection type:
   - **TLS**: Most common (recommended)
   - **mTLS**: Requires wallet download

4. Copy the connection string, which looks like:

```
(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=g9cf0f53d8eb092_tophatclandb_high.adb.oraclecloud.com))(security=(ssl_server_dn_match=yes)))
```

## Configuration

### Environment Variables

Add these to your `.env` file or environment:

#### Required Variables

```bash
# Oracle Database Configuration
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=YourSecurePassword123!
ORACLE_DSN=(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.us-chicago-1.oraclecloud.com))(connect_data=(service_name=your_service_name))(security=(ssl_server_dn_match=yes)))
```

#### Optional Variables (for wallet authentication)

```bash
# For mTLS wallet authentication
ORACLE_CONFIG_DIR=/path/to/wallet_directory/

# For Python 3.13+ with PEM wallet
ORACLE_WALLET_LOCATION=/path/to/ewallet.pem
ORACLE_WALLET_PASSWORD=YourWalletPassword
```

### Connection String Format

The DSN (Data Source Name) follows Oracle's Easy Connect Plus format:

```
(DESCRIPTION=
  (RETRY_COUNT=20)
  (RETRY_DELAY=3)
  (ADDRESS=(PROTOCOL=tcps)(PORT=1522)(HOST=your-db-host.oraclecloud.com))
  (CONNECT_DATA=(SERVICE_NAME=your_service_name))
  (SECURITY=(SSL_SERVER_DN_MATCH=yes))
)
```

**Important**: 
- Use `tcps` (TLS) protocol for secure connections
- Port `1522` is standard for Autonomous Database
- Remove line breaks when setting as environment variable

## Wallet Authentication

Oracle Autonomous Database supports two authentication methods:

### Method 1: TLS (No Wallet Required) ⭐ Recommended

This is the simplest method and requires only username, password, and DSN:

```bash
ORACLE_USER=tophat_bot
ORACLE_PASSWORD=YourPassword
ORACLE_DSN=your_connection_string_here
```

No additional wallet configuration needed!

### Method 2: mTLS (Requires Wallet)

If your database requires mutual TLS:

1. **Download Wallet**:
   - In OCI Console, go to your Autonomous Database
   - Click **DB Connection** > **Download Wallet**
   - Save and extract the ZIP file

2. **Configure Wallet Location**:

```bash
ORACLE_CONFIG_DIR=/path/to/wallet_directory/
```

3. **Update tnsnames.ora** (optional):
   - Edit `tnsnames.ora` in wallet directory
   - Use the alias in your connection

```bash
# Instead of full DSN, use TNS alias
ORACLE_DSN=tophatclandb_high
ORACLE_CONFIG_DIR=/path/to/wallet/
```

### Method 3: PEM Wallet (Python 3.13+)

For Python 3.13 and above, you can use PEM format:

```bash
ORACLE_WALLET_LOCATION=/path/to/ewallet.pem
ORACLE_WALLET_PASSWORD=YourWalletPassword
```

## Deployment Options

### Option 1: Local Development

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure `.env` file with Oracle credentials

3. Run the bot:

```bash
python bot.py
```

### Option 2: Docker Deployment

1. **Update docker-compose.yml**:

```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - DISCORD_BOT_TOKEN=${DISCORD_BOT_TOKEN}
      - GUILD_ID=${GUILD_ID}
      - ORACLE_USER=${ORACLE_USER}
      - ORACLE_PASSWORD=${ORACLE_PASSWORD}
      - ORACLE_DSN=${ORACLE_DSN}
      # Add other environment variables...
    volumes:
      # Mount wallet directory if using mTLS
      - ./wallet:/app/wallet:ro
    restart: unless-stopped
```

2. **If using wallet**, set config directory:

```bash
ORACLE_CONFIG_DIR=/app/wallet
```

3. **Build and run**:

```bash
docker-compose up -d
```

### Option 3: OCI Compute Instance

1. **Create OCI Compute Instance**
2. **Install Python and dependencies**:

```bash
sudo yum install python3 python3-pip
pip3 install -r requirements.txt
```

3. **Configure systemd service**:

Create `/etc/systemd/system/tophat-bot.service`:

```ini
[Unit]
Description=TophatC Clan Discord Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/TophatClanBot
EnvironmentFile=/home/opc/TophatClanBot/.env
ExecStart=/usr/bin/python3 /home/opc/TophatClanBot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

4. **Enable and start**:

```bash
sudo systemctl enable tophat-bot
sudo systemctl start tophat-bot
```

### Option 4: OCI Container Instances

1. **Build and push Docker image to OCI Registry**
2. **Create Container Instance** with environment variables
3. **Configure restart policy**: Always

## Testing

### Test Database Connection

Create a test script `test_oracle.py`:

```python
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("ORACLE_USER")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD")
CONNECT_STRING = os.getenv("ORACLE_DSN")

def test_connection():
    try:
        pool = oracledb.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=CONNECT_STRING,
            min=1,
            max=2
        )
        
        with pool.acquire() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                if result:
                    print(f"✅ Connected successfully! Query result: {result[0]}")
                    print(f"✅ Oracle version: {connection.version}")
                    return True
    except oracledb.Error as e:
        print(f"❌ Connection failed: {str(e)}")
        return False
    except Exception as e:
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_connection()
```

Run the test:

```bash
python test_oracle.py
```

Expected output:
```
✅ Connected successfully! Query result: 1
✅ Oracle version: 23.5.0.24.07
```

### Verify Tables Created

After starting the bot, verify tables were created:

```sql
-- Connect to database
SELECT table_name FROM user_tables ORDER BY table_name;

-- Should show:
-- CONFIG
-- MEMBERS
-- RAID_SUBMISSIONS
-- RANK_REQUIREMENTS
```

## Troubleshooting

### Connection Issues

#### Error: "ORA-12541: TNS:no listener"

**Cause**: Incorrect host or port in DSN

**Solution**: Verify connection string from OCI Console

#### Error: "ORA-01017: invalid username/password"

**Cause**: Incorrect credentials

**Solution**: Verify username and password are correct

#### Error: "ORA-12170: TNS:Connect timeout"

**Cause**: Network connectivity issue

**Solution**:
1. Check OCI network security lists allow port 1522
2. Verify VCN routing
3. Check firewall rules

### Wallet Issues

#### Error: "Could not open wallet"

**Cause**: Wallet directory path incorrect or permissions issue

**Solution**:
```bash
# Verify wallet directory exists
ls -la /path/to/wallet/

# Check permissions
chmod 700 /path/to/wallet/
chmod 600 /path/to/wallet/*
```

#### Error: "No such file or directory: 'tnsnames.ora'"

**Cause**: ORACLE_CONFIG_DIR not set correctly

**Solution**: Ensure wallet directory contains:
- `cwallet.sso`
- `tnsnames.ora`
- `sqlnet.ora`

### Performance Issues

#### Slow Queries

**Solution**: Enable connection pooling (already configured in `database_oracle.py`)

```python
pool = oracledb.create_pool(
    min=2,      # Minimum connections
    max=10,     # Maximum connections
    increment=1 # Connection increment
)
```

#### Connection Pool Exhausted

**Solution**: Increase pool size in `database_oracle.py`:

```python
pool = oracledb.create_pool(
    min=5,
    max=20,  # Increase from 10
    increment=2
)
```

## Database Differences from PostgreSQL

The Oracle adapter handles several database differences:

### Data Types
- `BIGINT` → `NUMBER(20)` for Discord IDs
- `SERIAL` → `NUMBER GENERATED ALWAYS AS IDENTITY`
- `TEXT` → `VARCHAR2` or `CLOB` for large text
- `BOOLEAN` → `NUMBER(1)` (0 = false, 1 = true)

### SQL Syntax
- `RETURNING` clause: `RETURNING column INTO :var`
- `LIMIT n` → `FETCH FIRST n ROWS ONLY`
- `INSERT ... ON CONFLICT` → `MERGE` statement
- Parameter binding: `$1, $2` → `:1, :2`

### Case Sensitivity
- Oracle converts identifiers to uppercase by default
- The adapter converts column names to lowercase in results

## Best Practices

1. **Use TLS authentication** (no wallet) when possible
2. **Create dedicated database user** (don't use ADMIN)
3. **Use connection pooling** (already configured)
4. **Enable automatic retries** (configured in DSN)
5. **Monitor connection pool** usage
6. **Regular backups** via OCI Console
7. **Use environment variables** for sensitive data
8. **Rotate passwords** regularly

## Additional Resources

- [Oracle Python Driver Documentation](https://python-oracledb.readthedocs.io/)
- [Oracle Autonomous Database Documentation](https://docs.oracle.com/en/cloud/paas/autonomous-database/)
- [Oracle Cloud Infrastructure Documentation](https://docs.oracle.com/en-us/iaas/Content/home.htm)

## Migration from PostgreSQL

If you're migrating from PostgreSQL:

1. **Export data** from PostgreSQL
2. **Create Oracle database** (tables auto-created on first run)
3. **Update environment variables** to use Oracle
4. **Import data** using SQL or migration script
5. **Test thoroughly** before production use

For detailed migration assistance, see `migrate_to_oracle.py` (coming soon).

## Security Notes

- **Never commit** `.env` file with credentials
- **Use secrets management** for production (OCI Vault)
- **Rotate credentials** regularly
- **Use least privilege** - create dedicated user
- **Enable audit logging** in Oracle ADB
- **Monitor access** via OCI Console

## Support

For issues specific to Oracle deployment:
1. Check this guide's troubleshooting section
2. Review Oracle Cloud logs in OCI Console
3. Verify network configuration
4. Check database connection limits
5. Consult Oracle documentation

---

**Need help?** Open an issue on the GitHub repository with:
- Error messages
- Oracle version
- Python version
- Connection method (TLS/mTLS)

