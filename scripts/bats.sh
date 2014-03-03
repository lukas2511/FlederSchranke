#!/bin/bash
screen -dmS bats sh -c 'python bats.py 2>&1 >> /home/root/logs/errorlogs/bats.log'
