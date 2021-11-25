#!/bin/bash
ps -ef|grep mydata | grep -v grep | awk '{print $2}' | xargs kill -9

ps -ef|grep 'tdx\/positions' | grep -v grep | awk '{print $2}' | xargs kill -9

