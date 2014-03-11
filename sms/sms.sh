#!/bin/bash
sleep 120 # 120 minuten warten, so dass alles andere schon läuft
while true; do
    gnokii --config /home/root/lichtschranke/sms/gnokiirc --getsms SM 0 end -a /home/root/logs/sms.txt -d 2> /dev/null
    sleep 600
done
