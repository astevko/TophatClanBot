# Oracle Database Integration Summary

## Overview

The TophatC Clan Bot now supports Oracle Autonomous Database as a production database option, in addition to PostgreSQL and SQLite. This integration enables enterprise-grade deployments on Oracle Cloud Infrastructure with the always-free tier.

## What Was Added

### 1. New Files Created

#### Core Database Module
- **`database_oracle.py`** - Complete Oracle database adapter with async support
  - Connection pooling (2-10 connections)
  - All CRUD operations for members, ranks, submissions, and config
  - Automatic table creation on first run
  - Full feature parity with PostgreSQL adapter

#### Testing & Migration Tools
- **`test_oracle_connection.py`** - Oracle connection test script
  - Validates credentials and connectivity
  - Tests query execution
  - Checks for existing tables
  - Provides helpful error messages

- **`migrate_postgres_to_oracle.py`** - PostgreSQL to Oracle migration tool
  - Exports all data from PostgreSQL
  - Imports to Oracle with proper type conversions
  - Handles duplicate detection
  - Verification of migrated data

#### Documentation
- **`ORACLE_DEPLOYMENT_GUIDE.md`** - Comprehensive Oracle setup guide
  - Prerequisites and requirements
  - Database setup instructions
  - Connection configuration
  - Wallet authentication options
  - Deployment scenarios
  - Troubleshooting guide

### 2. Modified Files

#### Configuration Updates
- **`config.py`** - Added Oracle configuration variables
  - `ORACLE_USER` - Database username
  - `ORACLE_PASSWORD` - Database password
  - `ORACLE_DSN` - Connection string
  - `ORACLE_CONFIG_DIR` - Optional wallet directory
  - `ORACLE_WALLET_LOCATION` - Optional PEM wallet path (Python 3.13+)
  - `ORACLE_WALLET_PASSWORD` - Optional wallet password
  - `USE_ORACLE` - Auto-detection flag

- **`bot.py`** - Updated database import logic
  - Priority: Oracle > PostgreSQL > SQLite
  - Automatic selection based on environment variables

- **`requirements.txt`** - Added Oracle driver
  - `oracledb>=2.0.0` - Official Oracle Python driver

- **`setup_example.env`** - Added Oracle configuration examples
  - Connection string templates
  - Wallet configuration options
  - Helpful comments

#### Documentation Updates
- **`README.md`** - Updated database section
  - Added Oracle as third database option
  - Explained database selection priority
  - Added migration scripts to backup section
  - Updated project structure

- **`DOCUMENTATION_INDEX.md`** - Added Oracle references
  - New database management section entry
  - New migration scripts
  - New use case scenarios
  - Updated file structure
  - Updated topic table

## Database Selection Priority

The bot automatically selects the database backend in this order:

1. **Oracle** - If `ORACLE_USER`, `ORACLE_PASSWORD`, and `ORACLE_DSN` are all set
2. **PostgreSQL** - If `DATABASE_URL` is set
3. **SQLite** - Default fallback for local development

## Key Features

### Connection Management
- **Connection Pooling**: 2-10 connections with automatic scaling
- **Automatic Retries**: Configured in DSN (retry_count=20, retry_delay=3)
- **TLS Support**: Secure connections without wallet (recommended)
- **Wallet Support**: Optional mTLS authentication
- **Python 3.13+ Support**: PEM wallet format

### Database Operations
- **Auto Schema Creation**: Tables created automatically on first run
- **Type Conversions**: Automatic handling of Oracle-specific types
  - `BIGINT` → `NUMBER(20)` for Discord IDs
  - `SERIAL` → `NUMBER GENERATED ALWAYS AS IDENTITY`
  - `TEXT` → `VARCHAR2` or `CLOB`
  - `BOOLEAN` → `NUMBER(1)` (0/1)
- **SQL Syntax Adaptation**: 
  - Parameterized queries use `:1, :2` instead of `$1, $2`
  - `LIMIT n` → `FETCH FIRST n ROWS ONLY`
  - `INSERT ... ON CONFLICT` → `MERGE` statement

### Error Handling
- Detailed error messages with Oracle error codes
- Helpful hints for common connection issues
- Graceful handling of duplicate entries
- Automatic fallback for existing tables

## Quick Start

### 1. Set Up Oracle Database

```bash
# Create Oracle Autonomous Database in OCI Console
# Use always-free tier (20 GB storage)
# Create application user (recommended)
```

### 2. Configure Environment

```bash
# Add to .env file
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=(description=(retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1522)(host=adb.region.oraclecloud.com))(connect_data=(service_name=your_service_name))(security=(ssl_server_dn_match=yes)))
```

### 3. Test Connection

```bash
python test_oracle_connection.py
```

Expected output:
```
✅ Connected successfully! Query result: 1
✅ Oracle version: 23.5.0.24.07
```

### 4. Run the Bot

```bash
python bot.py
```

The bot will automatically:
- Detect Oracle configuration
- Create connection pool
- Initialize database tables
- Start Discord bot

## Migration Path

### From PostgreSQL to Oracle

```bash
# 1. Configure Oracle in .env
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=your_connection_string

# 2. Test Oracle connection
python test_oracle_connection.py

# 3. Run migration (keeps PostgreSQL intact)
python migrate_postgres_to_oracle.py

# 4. Verify migration
python test_oracle_connection.py

# 5. Update .env to use Oracle (comment out DATABASE_URL)
# DATABASE_URL=...  # Comment this out

# 6. Start bot with Oracle
python bot.py
```

## Oracle-Specific Implementation Details

### Data Type Mappings

| PostgreSQL/SQLite | Oracle | Notes |
|-------------------|--------|-------|
| `BIGINT` | `NUMBER(20)` | For Discord IDs (19 digits) |
| `INTEGER` | `NUMBER(10)` | For points, ranks |
| `SERIAL` | `NUMBER GENERATED ALWAYS AS IDENTITY` | Auto-increment |
| `TEXT` | `VARCHAR2(n)` or `CLOB` | Based on expected length |
| `BOOLEAN` | `NUMBER(1)` | 0 = false, 1 = true |
| `TIMESTAMP` | `TIMESTAMP` | Direct mapping |

### SQL Syntax Differences

#### Parameterized Queries
```python
# PostgreSQL
cursor.execute("SELECT * FROM members WHERE discord_id = $1", [discord_id])

# Oracle
cursor.execute("SELECT * FROM members WHERE discord_id = :1", [discord_id])
```

#### LIMIT Queries
```sql
-- PostgreSQL
SELECT * FROM members ORDER BY points DESC LIMIT 10

-- Oracle
SELECT * FROM members ORDER BY points DESC FETCH FIRST 10 ROWS ONLY
```

#### UPSERT Operations
```sql
-- PostgreSQL
INSERT INTO config (key, value) VALUES ($1, $2)
ON CONFLICT (key) DO UPDATE SET value = $2

-- Oracle
MERGE INTO config c
USING (SELECT :1 AS key, :2 AS value FROM dual) src
ON (c.key = src.key)
WHEN MATCHED THEN UPDATE SET c.value = src.value
WHEN NOT MATCHED THEN INSERT (key, value) VALUES (src.key, src.value)
```

### Row to Dictionary Conversion

Oracle rows need to be converted to dictionaries manually:

```python
def _dict_from_row(cursor, row):
    """Convert Oracle row to dictionary using cursor description."""
    if row is None:
        return None
    columns = [col[0].lower() for col in cursor.description]
    return dict(zip(columns, row))
```

## Authentication Methods

### 1. TLS (Recommended) ⭐
- **No wallet required**
- Simplest configuration
- Just username, password, and DSN
- Uses `tcps` protocol on port 1522

### 2. mTLS (Mutual TLS)
- Requires wallet download from OCI
- More secure with certificate validation
- Set `ORACLE_CONFIG_DIR` to wallet directory
- Contains `cwallet.sso`, `tnsnames.ora`, `sqlnet.ora`

### 3. PEM Wallet (Python 3.13+)
- PEM format wallet file
- Set `ORACLE_WALLET_LOCATION` and `ORACLE_WALLET_PASSWORD`
- Newer Python versions only

## Performance Considerations

### Connection Pool Settings

Current configuration in `database_oracle.py`:
```python
pool = oracledb.create_pool(
    min=2,      # Minimum connections kept alive
    max=10,     # Maximum concurrent connections
    increment=1 # How many to add when scaling
)
```

### Recommended Adjustments

For **high-traffic servers** (1000+ members):
```python
min=5, max=20, increment=2
```

For **low-traffic servers** (<100 members):
```python
min=1, max=5, increment=1
```

## Security Best Practices

1. **Use dedicated database user** (not ADMIN)
2. **Grant minimal permissions** (CONNECT, RESOURCE)
3. **Use TLS authentication** when possible
4. **Never commit credentials** to version control
5. **Rotate passwords regularly**
6. **Use OCI Vault** for production secrets
7. **Enable Oracle audit logging**
8. **Monitor connection pool** usage

## Troubleshooting

### Common Issues

#### ORA-12541: TNS:no listener
**Solution**: Verify host and port in DSN from OCI Console

#### ORA-01017: Invalid username/password
**Solution**: Check credentials, ensure user exists in database

#### ORA-12170: TNS:Connect timeout
**Solution**: Check OCI network security lists allow port 1522

#### Connection pool exhausted
**Solution**: Increase `max` in pool configuration

### Debug Mode

Enable detailed logging:
```python
import logging
logging.getLogger("oracledb").setLevel(logging.DEBUG)
```

## Deployment Scenarios

### 1. Local Development
- Use SQLite (default)
- No Oracle configuration needed

### 2. Cloud Development/Staging
- Use Oracle free tier
- Configure TLS connection
- No wallet needed

### 3. Production
- Use Oracle Autonomous Database
- Consider mTLS with wallet for additional security
- Enable automatic backups in OCI Console
- Use OCI Vault for credential management

### 4. Docker Deployment
- Mount wallet directory if using mTLS
- Pass environment variables via docker-compose
- Use secrets management

## Cost Information

### Oracle Cloud Always Free Tier
- ✅ 2 Oracle Autonomous Databases
- ✅ 20 GB storage each
- ✅ 1 OCPU per database
- ✅ Automatic backups
- ✅ **Free forever** (not a trial)

Perfect for Discord bot production deployments!

## Future Enhancements

Potential improvements for future versions:

1. **Async Connection Pool**: Use `oracledb.create_pool_async()`
2. **Advanced Monitoring**: Connection pool metrics
3. **Automatic Failover**: Multiple Oracle endpoints
4. **Batch Operations**: Bulk inserts/updates
5. **Query Optimization**: Index recommendations
6. **Backup Automation**: Scheduled OCI exports

## Testing Checklist

Before going to production:

- [ ] Test connection with `test_oracle_connection.py`
- [ ] Verify tables created successfully
- [ ] Test member registration (`/link-roblox`)
- [ ] Test raid submission and approval
- [ ] Test points and promotion
- [ ] Test leaderboard
- [ ] Test config storage
- [ ] Monitor connection pool usage
- [ ] Verify Roblox sync works
- [ ] Test bot restart (reconnection)

## Support Resources

- **Oracle Documentation**: [python-oracledb.readthedocs.io](https://python-oracledb.readthedocs.io/)
- **OCI Documentation**: [docs.oracle.com](https://docs.oracle.com/en-us/iaas/Content/home.htm)
- **Deployment Guide**: `ORACLE_DEPLOYMENT_GUIDE.md`
- **Testing Script**: `test_oracle_connection.py`
- **Migration Tool**: `migrate_postgres_to_oracle.py`

## Summary

The Oracle integration provides a robust, enterprise-grade database option for the TophatC Clan Bot with:

✅ **Zero cost** (Always Free tier)  
✅ **Automatic backups** (managed by Oracle)  
✅ **High availability** (99.95% SLA)  
✅ **Scalability** (20 GB free storage)  
✅ **Security** (TLS/mTLS encryption)  
✅ **Easy setup** (3-step configuration)  
✅ **Feature parity** (all bot features supported)  
✅ **Migration tools** (from PostgreSQL)  

Perfect for production Discord bot deployments!

---

**Last Updated**: November 15, 2025  
**Integration Version**: 1.0.0  
**Tested with**: Oracle Database 23c, oracledb 2.0+

