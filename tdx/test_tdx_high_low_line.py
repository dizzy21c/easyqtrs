#!/usr/bin/python3.6
# -*- coding: utf-8 -*-
import sys
import os
import pandas as pd
from matplotlib import pyplot as plt
import test_tdx as tdx
from test_high_low_line import h_l_line, h_l_line_png
from test_baostock import read_k_day


def single_stock(p_data, ts_code, save_path: str, save_suffix='high_low_line_'):
    """
    处理单个股票的高低点数据，包含高点的的价格、日期、周期等，保存数据和图到指定的目录下.
    :param p_data: 数据文件路径
    :param save_suffix: 文件名称前缀
    :param save_path: 保存路径
    :param ts_code:
    :return:
    """
    if p_data is None:
        return False
    # 获取高低点数据,这里可以设置高低线的天数
    l_data = h_l_line(p_data, 89)
    if l_data is not None and len(l_data) > 0:
        # 数据保存在D盘下
        fn_png = '{}{}{}.png'.format(save_path, save_suffix, ts_code)
        fn_csv = '{}{}{}.csv'.format(save_path, save_suffix, ts_code)
        # 保存高低点图片
        h_l_line_png(l_data, ts_code, fn_png, show=True)
        # 保存高低点的表格数据
        l_data.to_csv(fn_csv, index=False)
        return True
    return False


if __name__ == "__main__":
    # 这里修改实际通达信文件导出的路径,第一个路径是数据路径,第二个是输出路径
    df_data = tdx.tdx_read_data_from_file('/home/tdx/test', '000859')
    single_stock(df_data, '000859', '/Users/huguohe/haojlwork/testa/')
    print("ok")
