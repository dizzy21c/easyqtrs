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
/opt/conda/bin/python tdx/positions_01_sina.py &
/opt/conda/bin/python tdx/positions_etf_sina.py &
/opt/conda/bin/python tdx/positions_01_mqtt.py &
/opt/conda/bin/python tdx/positions_etf_mqtt.py &

# python tdx_hcalc_new1.py -f tdx_lyqd,tdx_dqe_test_A01,tdx_dqe_xqc_A1 -b 2020-01-01 -e 2022-12-31 -r 2022-01-10 -t T -a all -s 0,0,50
