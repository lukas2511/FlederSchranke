#!/bin/bash
sleep 60
while true; do
    gnokii --config /home/root/lichtschranke/sms/gnokiirc --getsms SM 0 end -a /home/root/logs/sms.txt -d 2> /dev/null
    sleep 600
done
