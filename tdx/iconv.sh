#!/bin/bash
#echo $# 
#echo $*
for i in "$@"; do
  iconv --from-code=gb2312 --to-code=utf-8 "$i" >  "U$i"
  #rm $i 
done
#iconv --from-code=gb2312 --to-code=utf-8 21PP20210608.txt >  21PP20210608-u.txt
