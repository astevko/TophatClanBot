#!/bin/bash
# Connect to Oracle Autonomous Database via SQLcl

# Load credentials from .env file (handles .env without export statements)
set -a
source /home/opc/TophatClanBot/.env
set +a

export TNS_ADMIN=/home/opc/TophatClanBot/wallet_config

sql ${ORACLE_ADMIN_USER}/${ORACLE_ADMIN_PASSWORD}@perrydatabase_high
