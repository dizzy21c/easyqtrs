#!/bin/bash
ps -ef|grep mytest | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep mydata | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep mycalc | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep myworker | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep backtest | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep 'tdx\/positions' | grep -v grep | awk '{print $2}' | xargs kill -9

dt=`date +%H%M`
if [ $dt -gt "1500" ]; then
    ps -ef|grep 'tdx_hcalc' | grep -v grep | awk '{print $2}' | xargs kill -9
fi

