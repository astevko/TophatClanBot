

# Provision free tier instance
## create ssh key pair
ssh-keygen ...
use public key when creating the instance

## connecting to remote
make sure VNIC has public ip address checkbox clicked.

copy remote ip address

## create DNS A record for instance's public ip address

## create .ssh/config entry for new connection

# Provision an AI Autonomous Database

# connect local cli to remote instance

# connect instance cli to database
## configure
bash
sudo yum install java sqlci

download mTLS wallet from GUI, transfer to remote instance
scp Wallet_perrydatabase.zip perry.stevko.xyz:TophatClanBot/

mkdir -p /home/opc/TophatClanBot/wallet_config
unzip Wallet_perrydatabase.zip -d /home/opc/TophatClanBot/wallet_config

## login
sql /nolog
SQL> SET CLOUDCONFIG /home/opc/TophatClanBot/Wallet_perrydatabase.zip
SQL> CONNECT ADMIN@perrydatabase_high
Password? (**********?) ************
-- If successful, you should see "Connected."

## create user TOPHATCLAN_BOT

SQL> CREATE USER tophat_bot IDENTIFIED BY "YourSecurePassword123!";

SQL> GRANT CONNECT TO TOPHATCLAN_BOT;

Grant succeeded.

SQL> GRANT RESOURCE TO TOPHATCLAN_BOT;

Grant succeeded.

SQL> GRANT UNLIMITED TABLESPACE TO TOPHATCLAN_BOT;

Grant succeeded.

SQL> DISCONNECT;


# Testing it works...
cd TophatClanBot
uv run bot.py


# Setting up systemd to automatically run bot.py

sudo vi /etc/systemd/system/tophat-bot.service

```ini
[Unit]
Description=TophatC Clan Discord Bot
After=network.target

[Service]
Type=simple
User=opc
WorkingDirectory=/home/opc/TophatClanBot
EnvironmentFile=/home/opc/TophatClanBot/.env
ExecStart=/home/opc/.local/bin/uv run bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
sudo systemctl enable tophat-bot

sudo systemctl start tophat-bot
sudo systemctl stop tophat-bot
sudo journalctl -u tophat-bot -f
sudo systemctl status tophat-bot
