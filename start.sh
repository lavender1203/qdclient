#!/bin/bash
#killall python3
#python3 /root/qdclient/app.py &
#python3 /root/qdclient/start.py &
#python3 /root/qdclient/startGetHongbao.py &
#killall node
#node /root/qdclient/backend/tcaptcha_js/js/express.js
#ps -ef | grep start.py | grep -v grep | awk '{print $2}' | sudo xargs kill -9
#ps -ef | grep startGetHongbao.py | grep -v grep | awk '{print $2}' | sudo xargs kill -9
#ps -ef | grep run.sh | grep -v grep | awk '{print $2}' | sudo xargs kill -9
ps -ef | grep app.py | grep -v grep | awk '{print $2}' | sudo xargs kill -9
python3 /root/qdclient/app.py &
#python3 /root/qdclient/start.py &
#python3 /root/qdclient/startGetHongbao.py &
#cd /root/tcaptcha_puppeteer
#sh run.sh &
#cd -
