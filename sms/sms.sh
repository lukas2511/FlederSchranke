#!/bin/bash
sleep 120 # 120 minuten warten, so dass alles andere schon läuft
while true; do
    gnokii --config /home/root/lichtschranke/sms/gnokiirc --getsms SM 0 end -a /home/root/logs/sms.txt -d 2> /dev/null
    (echo -n $(date +%s)': '; (chat -V -s '' 'AT+CSQ' 'OK' '' > /dev/ttyUSB1 < /dev/ttyUSB1) 2>&1 | grep ^+CSQ | awk '{print $2}') >> /home/root/logs/csq.txt
    sleep 600
done
