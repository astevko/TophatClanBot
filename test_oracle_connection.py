"""
Test script for Oracle database connection
Based on Oracle's quick start guide
"""

import os

import oracledb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment
DB_USER = os.getenv("ORACLE_USER")
DB_PASSWORD = os.getenv("ORACLE_PASSWORD")
CONNECT_STRING = os.getenv("ORACLE_DSN")
CONFIG_DIR = os.getenv("ORACLE_CONFIG_DIR")
WALLET_LOCATION = os.getenv("ORACLE_WALLET_LOCATION")
WALLET_PASSWORD = os.getenv("ORACLE_WALLET_PASSWORD")


def run_app():
    try:
        # If THICK mode is needed, uncomment the following line.
        # oracledb.init_oracle_client()

        # Create connection pool parameters
        pool_params = {
            "user": DB_USER,
            "password": DB_PASSWORD,
            "dsn": CONNECT_STRING,
        }

        # Add optional wallet configuration if provided
        if CONFIG_DIR:
            pool_params["config_dir"] = CONFIG_DIR

        # If THIN mode is needed and your Python version is 3.13 and above
        if WALLET_LOCATION:
            pool_params["wallet_location"] = WALLET_LOCATION
        if WALLET_PASSWORD:
            pool_params["wallet_password"] = WALLET_PASSWORD

        print("Connecting to Oracle database...")
        print(f"User: {DB_USER}")
        print(f"DSN: {CONNECT_STRING[:50]}..." if len(CONNECT_STRING) > 50 else f"DSN: {CONNECT_STRING}")

        # Create connection pool
        pool = oracledb.create_pool(**pool_params)

        with pool.acquire() as connection:
            print("✅ Successfully connected to Oracle Database!")
            print(f"✅ Oracle version: {connection.version}")

            with connection.cursor() as cursor:
                # Test query
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                if result:
                    print(f"✅ Query test passed! Result: {result[0]}")

                # Check if tables exist
                print("\n📊 Checking for bot tables...")
                cursor.execute("""
                    SELECT table_name 
                    FROM user_tables 
                    WHERE table_name IN ('MEMBERS', 'RAID_SUBMISSIONS', 'RANK_REQUIREMENTS', 'CONFIG')
                    ORDER BY table_name
                """)

                tables = cursor.fetchall()
                if tables:
                    print("Found existing tables:")
                    for table in tables:
                        print(f"  - {table[0]}")
                else:
                    print("No bot tables found (will be created on first bot run)")

                print("\n✅ Connection test completed successfully!")
                return True

    except oracledb.Error as e:
        error_obj, = e.args
        print("\n❌ Oracle Database Error:")
        print(f"   Code: {error_obj.code}")
        print(f"   Message: {error_obj.message}")

        # Provide helpful hints based on error code
        if error_obj.code == 1017:
            print("\n💡 Hint: Invalid username or password. Please check your credentials.")
        elif error_obj.code == 12541:
            print("\n💡 Hint: Cannot reach the database. Check your DSN and network connectivity.")
        elif error_obj.code == 12170:
            print("\n💡 Hint: Connection timeout. Check firewall and network settings.")

        return False

    except Exception as e:
        print(f"\n❌ Unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("TophatC Clan Bot - Oracle Connection Test")
    print("=" * 60)
    print()

    # Validate required environment variables
    if not DB_USER or not DB_PASSWORD or not CONNECT_STRING:
        print("❌ Missing required environment variables!")
        print("\nPlease set the following in your .env file:")
        print("  - ORACLE_USER")
        print("  - ORACLE_PASSWORD")
        print("  - ORACLE_DSN")
        print("\nSee setup_example.env for configuration examples.")
        exit(1)

    success = run_app()

    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! Bot is ready to use Oracle database.")
    else:
        print("❌ Tests failed. Please check the errors above.")
    print("=" * 60)

