#!/bin/bash
/opt/conda/bin/python /root/QUANTAXIS/config/update_all.py
#tdx/get_baostock_data.py baosdk
#/opt/conda/bin/python tdx/get_baostock_data.py baosdk
#/opt/conda/bin/python tdx/get_baostock_data.py baosdk
/opt/conda/bin/python tdx_hcalc_eday_select.py -a etf-kj
/opt/conda/bin/python tdx_hcalc_eday_select.py -a index-tdx


