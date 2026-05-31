#!/bin/sh

set -e

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)

echo "Backup started $TIMESTAMP"

mkdir -p /backups/$TIMESTAMP

pg_dump -h db -U postgres postgres > /backups/$TIMESTAMP/db.sql

cp -r /app/images /backups/$TIMESTAMP/
cp -r /app/logs /backups/$TIMESTAMP/

mkdir -p /backups/$TIMESTAMP/config
cp /app/nginx.conf /backups/$TIMESTAMP/config/
cp /app/docker-compose.yml /backups/$TIMESTAMP/config/

tar -czf /backups/$TIMESTAMP.tar.gz -C /backups $TIMESTAMP
rm -rf /backups/$TIMESTAMP

echo "Backup done"