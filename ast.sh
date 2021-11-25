#!/bin/bash
# ps -ef|grep mydata2 | grep -v grep | awk '{print $2}' |xargs kill -9
# ps -ef|grep mycalc | grep -v grep | awk '{print $2}' |xargs kill -9
cd /root/code/easyquant/easyqtrs
./stop.sh
dt=`date +%H%M`
if [ $dt -lt "0930" ]; then
  rm -rf logs/*
fi
echo "start data-monitoring"
/opt/conda/bin/python mydata2.py &
echo "start calc-monitoring"
/opt/conda/bin/python tdx/positions_01.py &
/opt/conda/bin/python tdx/positions_etf.py &
