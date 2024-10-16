#!/bin/bash
source /root/TrafficBot/myenv/bin/activate
nohup python3 /root/TrafficBot/main.py > /dev/null 2>&1 &
