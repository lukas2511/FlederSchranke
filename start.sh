#!/bin/bash

if [ ! -e /tmp/screens/S-root/*wakeupcall* ]; then
    echo "Sending wakeupcall"
    cd /home/root/lichtschranke/wakeupcall
    ./start.sh
fi

if [ ! -e /tmp/screens/S-root/*sms* ]; then
    echo "Starting SMS-Reader"
    cd /home/root/lichtschranke/sms
    ./start.sh
fi

if [ ! -e /tmp/screens/S-root/*umtskeeper* ]; then
    echo "Starting 3G connection"
    cd /home/root/lichtschranke/3g
    ./start.sh
fi

if [ ! -e /tmp/screens/S-root/*openvpn* ]; then
    echo "Starting OpenVPN client"
    cd /home/root/lichtschranke/openvpn
    ./start.sh
fi

if [ ! -e /sys/class/gpio/gpio9 ]; then
    echo "Enabling Reset-Pin for Arduino"
    echo 9 > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio9/direction 
    echo 0 > /sys/class/gpio/gpio9/value
fi

if [ -e "/home/root/logs/uEnv.txt" ]; then
    if [ ! -e /tmp/screens/S-root/*weather* ]; then
        echo "Starting Weather-Logger"
        cd /home/root/lichtschranke/scripts
        ./weather.sh
    fi
    if [ ! -e /tmp/screens/S-root/*bats* ]; then
        echo "Starting Bat-Logger"
        cd /home/root/lichtschranke/scripts
        ./bats.sh
    fi
fi

