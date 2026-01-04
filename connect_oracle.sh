#!/bin/bash
# Connect to Oracle Autonomous Database via SQLcl

# Load credentials from .env file
source /home/opc/TophatClanBot/.env

sql /nolog <<EOF
SET CLOUDCONFIG /home/opc/TophatClanBot/Wallet_perrydatabase.zip
CONNECT ${ORACLE_ADMIN_USR}/${ORACLE_ADMIN_PASSWORD}@perrydatabase_high
EOF

