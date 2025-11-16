

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