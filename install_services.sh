#!/bin/bash
mount -o remount,rw /
cp /home/root/lichtschranke/*/*.service /lib/systemd/system/
systemctl --system daemon-reload
for service in /home/root/lichtschranke/*/*.service; do
    systemctl enable $(echo $service | cut -d'/' -f6)
done
mount -o remount,ro /
