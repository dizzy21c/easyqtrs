#!/bin/bash
mongo quantaxis -eval 'db.getCollectionNames() ' | grep realtime > db.txt
cut -d_ -f2 db.txt > db2.txt 
cut -d\" -f1 db2.txt > db3.txt

for line in `cat db3.txt`
do 
  #echo $line
  python tdx_hcalc_new1.py -f tdx_lyqd,tdx_dqe_test_A01,tdx_dqe_xqc_A1 -b 2020-01-01 -e 2021-12-31 -r $line -t B -a all -s 0,0,50
  docker restart docker_mgdb_1
done

#python tdx_hcalc_new1.py -f tdx_ltqd,tdx_dqe_xqc_A1 -b 2020-01-01 -e 2021-12-31 -r 2021-09-27 -t B -a all -s 0,50
#docker restart docker_mgdb_1
