#!/bin/bash
ps -ef|grep 'tdx\/positions' | grep -v grep | awk '{print $2}' | xargs kill -9
/opt/conda/bin/python tdx/positions_01.py &
/opt/conda/bin/python tdx/positions_etf.py &

