from easyquant import MongoIo
from easyquant.indicator.base import *
from easyquant.indicator.udf_formula import *

from pandas import Series,DataFrame
import pandas as pd
import numpy as np
rs=MongoIo()

# data_df = rs.get_day_df('000001', startpos = 1000)
# data_df = data_df.set_index(['date'], drop=False)

def klineplot(data_df,*avg_line):
    # from IPython.core.display import display, HTML
    from pyecharts import Kline
    from pyecharts import Line
    from pyecharts import Bar
    from pyecharts import Overlap
    from pyecharts import Grid
    # import warnings
    import pandas as pd
    # for i in range(len(data_df)):
    #     if data_df["vol"][i] < 0:
    #         data_df["vol"][i]=0

    if ("time" in data_df) and ("date" in data_df):
        date=data_df["date"]+" "+data_df["time"]
    if "time" not in data_df.columns:
        date=data_df["date"]
    if "date" not in data_df.columns:
        date=data_df["time"]
    x=[]
    for i in range(len(data_df)):
        y=[data_df["open"][i],data_df["close"][i],data_df["low"][i],data_df["high"][i]]
        x.append(y)
    kline = Kline()
    kline.add("high",date,x,
            tooltip_tragger="axis",is_datazoom_show=True,tooltip_axispointer_type='cross',
            is_legend_show=False,is_more_utils=True,yaxis_min=(min(data_df["low"])-(max(data_df["high"])-min(data_df["low"]))/4))

    line2=Line()
    p_list=["open","close","low"]
    for i in p_list:
        line2.add(i,date,data_df[i],tooltip_tragger="axis",line_opacity=0)

    ma_list=avg_line
    print(ma_list)
    if len(ma_list)>0:
        line1=Line()
        for ma in ma_list:
            print(ma)
            # data_df['MA_' + str(ma)] = pd.Series.rolling(data_df['close'], ma).mean()
            data_df['MA_' + str(ma)] = HHV(data_df.close, ma)
            line1.add("MA_%r"%ma,date,data_df['MA_' + str(ma)],tooltip_tragger="axis")

    bar = Bar()
    bar.add("vol", date, data_df["vol"],tooltip_tragger="axis",is_legend_show=False,is_yaxis_show=False,yaxis_max=5*max(data_df["vol"]))

    overlap = Overlap() #width="80%", height=800)
    overlap.add(kline)
    # overlap.add(line2)
    if len(ma_list)>0:
        overlap.add(line1)
    # overlap.add(bar,yaxis_index=1, is_add_yaxis=True)

    # grid = Grid()
    grid = Grid(width=1360, height=700, page_title='QUANTAXIS')
    # grid.add(overlap, grid_top="30%")
    grid.add(bar, grid_top="50%")
    grid.add(overlap, grid_bottom="20%")


    # overlap.render("test.html")
    grid.render("test.html")
    # display(HTML(overlap._repr_html_()))
    # warnings.filterwarnings("ignore")

data_df = rs.get_stock_day('000001', st_start='2010-01-01')
# data_df = data_df.set_index(['date'], drop=False)

klineplot(data_df, 5, 10)