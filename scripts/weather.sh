#!/bin/bash
screen -dmS weather sh -c 'python weather.py 2>&1 >> /home/root/logs/errorlogs/weather.log'
