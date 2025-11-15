"""
Migration script to migrate data from PostgreSQL to Oracle
This script exports data from PostgreSQL and imports it into Oracle database.
"""

import asyncio
import os

import asyncpg
import oracledb
from dotenv import load_dotenv

load_dotenv()


async def export_from_postgres():
    """Export all data from PostgreSQL database."""
    print("Connecting to PostgreSQL...")
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return None

    conn = await asyncpg.connect(database_url)

    try:
        print("✅ Connected to PostgreSQL")
        print("\n📤 Exporting data from PostgreSQL...")

        data = {}

        # Export members
        print("  - Exporting members...")
        rows = await conn.fetch("SELECT * FROM members ORDER BY created_at")
        data['members'] = [dict(row) for row in rows]
        print(f"    ✅ Exported {len(data['members'])} members")

        # Export rank_requirements
        print("  - Exporting rank_requirements...")
        rows = await conn.fetch("SELECT * FROM rank_requirements ORDER BY rank_order")
        data['rank_requirements'] = [dict(row) for row in rows]
        print(f"    ✅ Exported {len(data['rank_requirements'])} ranks")

        # Export raid_submissions
        print("  - Exporting raid_submissions...")
        rows = await conn.fetch("SELECT * FROM raid_submissions ORDER BY timestamp")
        data['raid_submissions'] = [dict(row) for row in rows]
        print(f"    ✅ Exported {len(data['raid_submissions'])} submissions")

        # Export config
        print("  - Exporting config...")
        rows = await conn.fetch("SELECT * FROM config")
        data['config'] = [dict(row) for row in rows]
        print(f"    ✅ Exported {len(data['config'])} config entries")

        return data

    finally:
        await conn.close()
        print("Closed PostgreSQL connection")


def import_to_oracle(data):
    """Import data into Oracle database."""
    print("\nConnecting to Oracle...")

    oracle_user = os.getenv("ORACLE_USER")
    oracle_password = os.getenv("ORACLE_PASSWORD")
    oracle_dsn = os.getenv("ORACLE_DSN")
    oracle_config_dir = os.getenv("ORACLE_CONFIG_DIR")

    if not all([oracle_user, oracle_password, oracle_dsn]):
        print("❌ Oracle credentials not found in environment variables")
        print("   Required: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN")
        return False

    pool_params = {
        "user": oracle_user,
        "password": oracle_password,
        "dsn": oracle_dsn,
    }

    if oracle_config_dir:
        pool_params["config_dir"] = oracle_config_dir

    try:
        pool = oracledb.create_pool(**pool_params)
        connection = pool.acquire()

        print("✅ Connected to Oracle")
        print("\n📥 Importing data to Oracle...")

        cursor = connection.cursor()

        # Import rank_requirements first (referenced by members)
        print(f"  - Importing {len(data['rank_requirements'])} ranks...")
        for rank in data['rank_requirements']:
            try:
                cursor.execute("""
                    INSERT INTO rank_requirements 
                    (rank_order, rank_name, points_required, roblox_group_rank_id, admin_only)
                    VALUES (:1, :2, :3, :4, :5)
                """, [
                    rank['rank_order'],
                    rank['rank_name'],
                    rank['points_required'],
                    rank['roblox_group_rank_id'],
                    1 if rank['admin_only'] else 0
                ])
            except oracledb.IntegrityError:
                # Rank already exists, skip
                pass
        connection.commit()
        print("    ✅ Ranks imported")

        # Import members
        print(f"  - Importing {len(data['members'])} members...")
        imported_members = 0
        for member in data['members']:
            try:
                cursor.execute("""
                    INSERT INTO members 
                    (discord_id, roblox_username, current_rank, points, created_at)
                    VALUES (:1, :2, :3, :4, :5)
                """, [
                    member['discord_id'],
                    member['roblox_username'],
                    member['current_rank'],
                    member['points'],
                    member['created_at']
                ])
                imported_members += 1
            except oracledb.IntegrityError:
                print(f"    ⚠️  Skipping member {member['discord_id']} (already exists)")
        connection.commit()
        print(f"    ✅ Imported {imported_members} members")

        # Import raid_submissions
        print(f"  - Importing {len(data['raid_submissions'])} submissions...")
        imported_submissions = 0
        for submission in data['raid_submissions']:
            try:
                # Note: submission_id is auto-generated in Oracle
                cursor.execute("""
                    INSERT INTO raid_submissions 
                    (submitter_id, participants, start_time, end_time, image_url, 
                     status, points_awarded, admin_id, timestamp)
                    VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
                """, [
                    submission['submitter_id'],
                    submission['participants'],
                    submission['start_time'],
                    submission['end_time'],
                    submission['image_url'],
                    submission['status'],
                    submission['points_awarded'],
                    submission['admin_id'],
                    submission['timestamp']
                ])
                imported_submissions += 1
            except Exception as e:
                print(f"    ⚠️  Error importing submission {submission.get('submission_id')}: {e}")
        connection.commit()
        print(f"    ✅ Imported {imported_submissions} submissions")

        # Import config
        print(f"  - Importing {len(data['config'])} config entries...")
        for config_entry in data['config']:
            cursor.execute("""
                MERGE INTO config c
                USING (SELECT :1 AS key, :2 AS value FROM dual) src
                ON (c.key = src.key)
                WHEN MATCHED THEN
                    UPDATE SET c.value = src.value
                WHEN NOT MATCHED THEN
                    INSERT (key, value) VALUES (src.key, src.value)
            """, [
                config_entry['key'],
                config_entry['value']
            ])
        connection.commit()
        print("    ✅ Config imported")

        # Verify import
        print("\n📊 Verifying import...")
        cursor.execute("SELECT COUNT(*) FROM members")
        member_count = cursor.fetchone()[0]
        print(f"  - Members in Oracle: {member_count}")

        cursor.execute("SELECT COUNT(*) FROM rank_requirements")
        rank_count = cursor.fetchone()[0]
        print(f"  - Ranks in Oracle: {rank_count}")

        cursor.execute("SELECT COUNT(*) FROM raid_submissions")
        submission_count = cursor.fetchone()[0]
        print(f"  - Submissions in Oracle: {submission_count}")

        pool.release(connection)
        print("\n✅ Migration completed successfully!")
        return True

    except oracledb.Error as e:
        error_obj, = e.args
        print("\n❌ Oracle Error:")
        print(f"   Code: {error_obj.code}")
        print(f"   Message: {error_obj.message}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main migration function."""
    print("=" * 70)
    print("PostgreSQL to Oracle Migration Tool")
    print("=" * 70)
    print()
    print("⚠️  WARNING: This will import data into your Oracle database.")
    print("   Make sure you have:")
    print("   1. Backed up your PostgreSQL database")
    print("   2. Configured Oracle credentials in .env")
    print("   3. Initialized Oracle database (run bot once or use test script)")
    print()

    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Migration cancelled.")
        return

    print()

    # Step 1: Export from PostgreSQL
    data = await export_from_postgres()
    if not data:
        print("\n❌ Failed to export data from PostgreSQL")
        return

    # Step 2: Import to Oracle
    success = import_to_oracle(data)

    print("\n" + "=" * 70)
    if success:
        print("✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Update your .env file to use Oracle credentials")
        print("2. Test the bot with Oracle: python test_oracle_connection.py")
        print("3. Start the bot: python bot.py")
        print("\nNote: The bot will automatically use Oracle if ORACLE_USER is set.")
    else:
        print("❌ Migration failed. Please check the errors above.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())

