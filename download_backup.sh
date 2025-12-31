#!/bin/bash
# Usage: download_backup.sh <host> <password> <expert_password> <backup_file> <output_file>

HOST=$1
PASSWORD=$2
EXPERT_PASSWORD=$3
BACKUP_FILE=$4
OUTPUT_FILE=$5

# Use sshpass and a here-document to handle the interactive session
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o PubkeyAuthentication=no -o PreferredAuthentications=password -o KexAlgorithms=+diffie-hellman-group14-sha1 -o HostKeyAlgorithms=+ssh-rsa admin@$HOST << ENDSSH | grep "^[A-Za-z0-9+/]\{60,\}" | base64 -d > "$OUTPUT_FILE"
expert
$EXPERT_PASSWORD
base64 /var/CPbackup/backups/$BACKUP_FILE
exit
ENDSSH

if [ -s "$OUTPUT_FILE" ]; then
    echo "Successfully downloaded $(stat -c%s "$OUTPUT_FILE") bytes to $OUTPUT_FILE"
    exit 0
else
    echo "Failed to download backup file"
    exit 1
fi
