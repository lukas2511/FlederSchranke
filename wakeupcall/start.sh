#!/bin/bash
if [ -e "config.py" ]; then
    screen -dmS wakeupcall python wakeupcall.py
fi
