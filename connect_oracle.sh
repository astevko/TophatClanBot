#!/bin/bash
# Connect to Oracle Autonomous Database via SQLcl

# Load credentials from .env file
source /home/opc/TophatClanBot/.env

# Create a login script that sets up the connection
export TNS_ADMIN=/home/opc/TophatClanBot/wallet_config

sql ${ORACLE_ADMIN_USR}/${ORACLE_ADMIN_PASSWORD}@perrydatabase_high

