# coding: utf-8

import codecs
import copy
import csv
import datetime
import os
import struct
import sys
import timeit

def get_file(file_name):
    for line in open('config', 'r', encoding='utf8'):
        d = line.replace('\\\\', '/').replace('\\', '/').strip().strip('/\\')
        if d != '':
            f = d + '/' + file_name
            if os.path.exists(f):
                return f
    return None


def read_file(file_name: str, stock_code: str):
    if not file_name:
        return []
    data_list = []
    with open(file_name, 'rb') as stock_file:
        buffer = stock_file.read()  # 读取数据到缓存
        total_size = len(buffer)
        row_size = 32  # 通信达day数据，每32个字节一组数据
        for seg in range(0, total_size, row_size):  # 步长为32遍历buffer
            row = list(struct.unpack('IIIIIfII', buffer[seg: seg + row_size]))
            row[1] = row[1] / 100
            row[2] = row[2] / 100
            row[3] = row[3] / 100
            row[4] = row[4] / 100
            row.pop()  # 移除最后无意义字段
            row.insert(0, stock_code)
            data_list.append(row)
    return data_list


def analysis(data: list):
    if len(data) == 0:
        return [], []
    columns = ['code', 'tradeDate', 'open', 'high', 'low', 'close', 'amount', 'vol']
    data_with_empty = [columns]
    data_with_complete = [columns]
    pre_row = []
    stock_date = datetime.datetime.strptime(str(data[0][1]), '%Y%m%d').date()
    for row in data:
        if str(row[1]) == str(stock_date).replace('-', ''):
            pre_row = copy.deepcopy(row)
            data_with_empty.append(row)
            data_with_complete.append(row)
            stock_date = stock_date + datetime.timedelta(1)
        else:
            while int(str(stock_date).replace('-', '')) < row[1]:
                pre_row = copy.deepcopy(pre_row)
                pre_row[1] = int(str(stock_date).replace('-', ''))
                data_with_complete.append(pre_row)
                stock_date = stock_date + datetime.timedelta(1)
            pre_row = copy.deepcopy(row)
            data_with_empty.append(row)
            data_with_complete.append(row)
            stock_date = stock_date + datetime.timedelta(1)
    return data_with_empty, data_with_complete


def save_data(data_with_empty: list, data_with_complete: list, file_name: str):
    write_to_csv(file_name + '.append.csv', data_with_complete)
    write_to_csv(file_name + '.csv', data_with_empty)


def write_to_csv(file_name, data_list):  # file_name为写入CSV文件的路径，datas为要写入数据列表
    if len(data_list) < 2:
        return
    file_csv = codecs.open(file_name, 'w', 'utf-8')  # 追加
    writer = csv.writer(file_csv, delimiter=',', quotechar=' ', quoting=csv.QUOTE_MINIMAL)
    for line in data_list:
        writer.writerow(line)
    file_csv.close()


def run_(code: str):
    file_name = 'sh{0}.day'.format(code)
    f = get_file(file_name)
    if f:
        print('找到文件 {0}'.format(f))
    else:
        print('没有找到文件 {0}'.format(file_name))
    data_with_empty, data_with_complete = analysis(read_file(f, code))
    save_data(data_with_empty, data_with_complete, file_name)

    file_name = 'sz{0}.day'.format(code)
    f = get_file(file_name)
    if f:
        print('找到文件 {0}'.format(f))
    else:
        print('没有找到文件 {0}'.format(file_name))
    data_with_empty, data_with_complete = analysis(read_file(f, code))
    save_data(data_with_empty, data_with_complete, file_name)
    print('运行结束，回车退出')
    input()


def run_all():
    for line in open('config', 'r', encoding='utf8'):
        d = line.replace('\\\\', '/').replace('\\', '/').strip().strip('/\\')
        if d == '':
            continue
        files = os.listdir(d)
        for file in files:
            if not file.endswith('.day'):
                continue
            code = file.replace('sh', '').replace('sz', '').replace('.day', '')
            file_path = os.path.join(d, file)
            data_with_empty, data_with_complete = analysis(read_file(file_path, code))
            save_data(data_with_empty, data_with_complete, file)
            print(file_path)
    print('分析结束，回车退出')
    input()


if __name__ == '__main__':
    argc = len(sys.argv)
    if argc < 2:
        print('请输入股票代码，回车退出')
        input()
    elif argc == 2:
        if sys.argv[1] == 'all':
            run_all()
        else:
            run_(sys.argv[1])
