#!/bin/bash
ps -ef|grep 'tdx\/positions' | grep -v grep | awk '{print $2}' | xargs kill -9
/opt/conda/bin/python tdx/positions_01_sina.py &
/opt/conda/bin/python tdx/positions_01_mqtt.py &
/opt/conda/bin/python tdx/positions_etf_sina.py &
/opt/conda/bin/python tdx/positions_etf_mqtt.py &

