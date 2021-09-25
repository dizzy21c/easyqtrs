#!/bin/bash
ps -ef|grep mydata | grep -v grep | awk '{print $2}' |xargs kill -9
ps -ef|grep myworker | grep -v grep | awk '{print $2}' |xargs kill -9
cd /home/zhangjx/backup/bk/easyquant
dt=`date +%H%M`
if [ $dt -lt "0930" ]; then
  rm -rf logs/*
fi
# echo "calc top-codes..."
# /home/zhangjx/anaconda3/bin/python codelist_utils.py --code_type=top-codes
echo "start data-monitoring"
/home/zhangjx/anaconda3/bin/python mydata.py  &
#echo "start data-worker"
#/home/zhangjx/anaconda3/bin/python myworker.py data-worker &
#echo "start index-worker"
#/home/zhangjx/anaconda3/bin/python myworker.py index-worker &
echo "start position-worker"
/home/zhangjx/anaconda3/bin/python myworker.py position-worker &
echo "start top-worker"
/home/zhangjx/anaconda3/bin/python myworker.py top-worker &
