#!/bin/bash

ssh root@10.8.0.3 mount -o remount,rw /

rsync \
    --archive \
    ~/Projects/Bat-Projects/Lichtschranke/ \
    -e ssh \
    root@10.8.0.3:/home/root/lichtschranke/ \
    --progress \
    --exclude '*.dtbo' \
    --exclude '.git' \
    --delete

ssh root@10.8.0.3 mount -o remount,ro /
