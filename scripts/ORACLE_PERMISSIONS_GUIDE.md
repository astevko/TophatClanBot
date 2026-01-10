# Oracle Database Permissions Guide

This guide explains what permissions your Oracle bot user needs and how to grant them.

## Required Permissions

Your bot user needs the following permissions to successfully run the schema setup script:

### Basic Permissions (Usually Already Granted)
- **CONNECT** - Allows the user to connect to the database
- **RESOURCE** - Allows creating tables, indexes, and other database objects
- **UNLIMITED TABLESPACE** - Allows creating tables without specifying tablespace

### Additional Permissions (Required for Auto-Increment)
- **CREATE SEQUENCE** - Needed for creating sequences (used as fallback for IDENTITY)
- **CREATE TRIGGER** - Needed for creating triggers (used as fallback for IDENTITY)
- **CREATE PROCEDURE** - Optional but recommended for future functionality

## How to Grant Permissions

### Step 1: Connect as ADMIN

```sql
sql /nolog
SQL> SET CLOUDCONFIG /path/to/your/Wallet_database.zip
SQL> CONNECT ADMIN@your_database_high
Password? (enter your ADMIN password)
```

### Step 2: Grant Permissions

Replace `tophat_bot` with your actual bot username:

```sql
-- Basic privileges
GRANT CONNECT TO tophat_bot;
GRANT RESOURCE TO tophat_bot;
GRANT UNLIMITED TABLESPACE TO tophat_bot;

-- Additional privileges for auto-increment support
GRANT CREATE SEQUENCE TO tophat_bot;
GRANT CREATE TRIGGER TO tophat_bot;
GRANT CREATE PROCEDURE TO tophat_bot;

COMMIT;
```

### Step 3: Verify Permissions

Check what privileges your bot user has:

```sql
SELECT privilege 
FROM dba_sys_privs 
WHERE grantee = UPPER('tophat_bot')
ORDER BY privilege;
```

You should see at least:
- CREATE SEQUENCE
- CREATE SESSION (from CONNECT role)
- CREATE TABLE (from RESOURCE role)
- CREATE TRIGGER
- CREATE PROCEDURE

### Step 4: Test as Bot User

Disconnect and reconnect as your bot user to test:

```sql
DISCONNECT;
CONNECT tophat_bot@your_database_high
Password? (enter bot user password)

-- Test creating a sequence
CREATE SEQUENCE test_seq START WITH 1;
DROP SEQUENCE test_seq;

-- If this works, you have the right permissions!
```

## Quick Reference: All Commands at Once

```sql
-- Connect as ADMIN first!
CONNECT ADMIN@your_database_high;

-- Grant all required permissions
GRANT CONNECT TO tophat_bot;
GRANT RESOURCE TO tophat_bot;
GRANT UNLIMITED TABLESPACE TO tophat_bot;
GRANT CREATE SEQUENCE TO tophat_bot;
GRANT CREATE TRIGGER TO tophat_bot;
GRANT CREATE PROCEDURE TO tophat_bot;

COMMIT;
```

## What Each Permission Does

| Permission | Purpose |
|------------|---------|
| **CONNECT** | Allows user to connect to the database |
| **RESOURCE** | Allows creating tables, indexes, views, sequences, procedures, triggers |
| **UNLIMITED TABLESPACE** | Allows creating objects without specifying a tablespace |
| **CREATE SEQUENCE** | Allows creating sequences for auto-increment IDs |
| **CREATE TRIGGER** | Allows creating triggers for automatic ID generation |
| **CREATE PROCEDURE** | Allows creating stored procedures (optional) |

## Troubleshooting

### Error: ORA-01031: insufficient privileges

**Cause**: The bot user doesn't have the required privileges.

**Solution**: 
1. Make sure you're connected as ADMIN (or another DBA user)
2. Run the grant commands above
3. Verify with the SELECT query
4. Disconnect and reconnect as the bot user

### Error: ORA-00942: table or view does not exist

**Cause**: The table wasn't created due to insufficient privileges.

**Solution**: 
1. Grant the permissions above
2. Re-run the schema setup script: `@scripts/setup_oracle_schema.sql`

### Error: ORA-01408: such column list already indexed

**Cause**: This is normal - the UNIQUE constraint on `roblox_username` automatically creates an index.

**Solution**: This is not an error - the script handles this gracefully.

## After Granting Permissions

Once you've granted the permissions:

1. **Re-run the schema setup script**:
   ```sql
   CONNECT tophat_bot@your_database_high;
   SET SERVEROUTPUT ON;
   @scripts/setup_oracle_schema.sql
   ```

2. **Or run the helper script to add sequence/trigger** (if table was created without auto-increment):
   ```sql
   CONNECT tophat_bot@your_database_high;
   SET SERVEROUTPUT ON;
   @scripts/add_raid_submissions_sequence.sql
   ```

3. **Test the bot** - it should now be able to create raid submissions successfully!

## Oracle Autonomous Database Notes

In Oracle Autonomous Database:
- The ADMIN user has all privileges by default
- Application users need explicit grants (they don't inherit from ADMIN)
- Some advanced privileges may be restricted for security
- The RESOURCE role may not include CREATE SEQUENCE/TRIGGER in all configurations

If you're using Autonomous Database and still getting permission errors after granting these privileges, check:
1. You're using the correct username (case-sensitive in some contexts)
2. You've committed the grants (COMMIT;)
3. You've reconnected as the bot user to refresh privileges


