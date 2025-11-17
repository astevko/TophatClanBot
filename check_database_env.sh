#!/bin/bash
# Quick script to check which database the bot is configured to use

echo "========================================"
echo "Database Environment Check"
echo "========================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ ERROR: .env file not found!"
    echo "   Create one from setup_example.env"
    exit 1
fi

# Source the .env file
set -a
source .env
set +a

# Check Oracle configuration
echo "Oracle Configuration:"
if [ -n "$ORACLE_USER" ] && [ -n "$ORACLE_PASSWORD" ] && [ -n "$ORACLE_DSN" ]; then
    echo "  ✅ USE_ORACLE: true"
    echo "  📊 ORACLE_USER: $ORACLE_USER"
    echo "  📊 ORACLE_DSN: ${ORACLE_DSN:0:50}..."
    
    if [ -n "$ORACLE_CONFIG_DIR" ]; then
        echo "  📂 ORACLE_CONFIG_DIR: $ORACLE_CONFIG_DIR"
        if [ -d "$ORACLE_CONFIG_DIR" ]; then
            echo "     ✅ Wallet directory exists"
            if [ -f "$ORACLE_CONFIG_DIR/cwallet.sso" ]; then
                echo "     ✅ Wallet files found"
            else
                echo "     ⚠️  Wallet files missing!"
            fi
        else
            echo "     ❌ Wallet directory not found!"
        fi
    fi
else
    echo "  ❌ USE_ORACLE: false (credentials not fully configured)"
    if [ -z "$ORACLE_USER" ]; then echo "     Missing: ORACLE_USER"; fi
    if [ -z "$ORACLE_PASSWORD" ]; then echo "     Missing: ORACLE_PASSWORD"; fi
    if [ -z "$ORACLE_DSN" ]; then echo "     Missing: ORACLE_DSN"; fi
fi

echo ""
echo "PostgreSQL Configuration:"
if [ -n "$DATABASE_URL" ]; then
    echo "  📊 DATABASE_URL: ${DATABASE_URL:0:30}..."
else
    echo "  ❌ DATABASE_URL: not set"
fi

echo ""
echo "SQLite (Fallback):"
if [ -n "$ORACLE_USER" ] && [ -n "$ORACLE_PASSWORD" ] && [ -n "$ORACLE_DSN" ]; then
    echo "  ⏭️  SQLite will NOT be used (Oracle configured)"
elif [ -n "$DATABASE_URL" ]; then
    echo "  ⏭️  SQLite will NOT be used (PostgreSQL configured)"
else
    echo "  ⚠️  SQLite WILL be used (no production database configured)"
    if [ -f "tophat_clan.db" ]; then
        SIZE=$(du -h tophat_clan.db | cut -f1)
        echo "     Database file: tophat_clan.db ($SIZE)"
    else
        echo "     ❌ Database file does not exist!"
    fi
fi

echo ""
echo "========================================"
echo "Recommendation:"
echo "========================================"

if [ -n "$ORACLE_USER" ] && [ -n "$ORACLE_PASSWORD" ] && [ -n "$ORACLE_DSN" ]; then
    echo "✅ Bot is configured to use Oracle (production)"
    echo "   Run: uv run python test_oracle_connection.py"
elif [ -n "$DATABASE_URL" ]; then
    echo "✅ Bot is configured to use PostgreSQL (production)"
else
    echo "⚠️  Bot is configured to use SQLite (local development)"
    echo "   For production, configure Oracle or PostgreSQL in .env"
fi

echo ""

