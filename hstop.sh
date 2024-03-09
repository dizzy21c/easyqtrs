#!/bin/bash
ps -ef|grep tdx_hcalc_new1| grep -v grep | awk '{print $2}' | xargs kill -9

