import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import mpl_finance as mpf
from matplotlib import gridspec
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSignal
import pandas as pd
from pandas import DataFrame
from easyquant import MongoIo

class KMplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        FigureCanvas.__init__(self, self.fig)
        spec = gridspec.GridSpec(4, 1, height_ratios=[3, 1, 1, 1])
        self.ax1 = self.fig.add_subplot(spec[0])
        self.ax2 = self.fig.add_subplot(spec[1])
        self.ax3 = self.fig.add_subplot(spec[2])
        self.ax4 = self.fig.add_subplot(spec[3])
        self.setParent(parent)
        self.k_text = ['十字星', '两只乌鸦', '三只乌鸦', '三内部上涨和下跌', '三线打击',
                       '三外部上涨和下跌', '南方三星', '三个白兵', '弃婴', '大敌当前',
                       '捉腰带线', '脱离', '收盘缺影线', '藏婴吞没', '反击线'
            , '乌云压顶', '蜻蜓十字/T形十字', '吞噬模式', '十字暮星', '暮星',
                       '向上/下跳空并列阳线', '墓碑十字/倒T十字', '锤头', '上吊线', '母子线',
                       '十字孕线', '风高浪大线', '陷阱', '修正陷阱', '家鸽',
                       '三胞胎乌鸦', '颈内线', '倒锤头', '反冲形态', '由较长缺影线决定的反冲形态',
                       '停顿形态', '条形三明治', '探水竿', '跳空并列阴阳线', '插入',
                       '三星', '奇特三河床', '向上跳空的两只乌鸦', '上升/下降跳空三法']

        FigureCanvas.updateGeometry(self)

    def start_staict_plot(self, df, method="CDLDOJISTAR", numb=0):
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        self.fig.canvas.draw_idle()
        mytalib = talib
        f = getattr(mytalib, method)
        df['date'] = pd.to_datetime(df['date'])
        df['date'] = df['date'].apply(lambda x: x.strftime('%Y-%m-%d'))
        mpf.candlestick2_ochl(self.ax1, df["open"], df["close"], df["high"], df["low"], width=0.6, colorup='r',
                              colordown='green',
                              alpha=1.0)
        df['star'] = f(df['open'].values, df['high'].values, df['low'].values, df['close'].values)

        pattern = df[(df['star'] == 100) | (df['star'] == -100)]
        for key, val in df.items():
            for index, today in pattern.iterrows():
                x_posit = df.index.get_loc(index)
                self.ax1.annotate("{}\n{}".format(self.k_text[numb], today["date"]), xy=(x_posit, today["high"]),
                                  xytext=(0, pattern["close"].mean()), xycoords="data",
                                  fontsize=8, textcoords="offset points",
                                  arrowprops=dict(arrowstyle="simple", color="r"))
        df["SMA5"] = df["close"].rolling(5).mean()
        df["SMA10"] = df["close"].rolling(10).mean()
        df["SMA30"] = df["close"].rolling(30).mean()
        df["SMA60"] = df["close"].rolling(60).mean()
        self.ax1.plot(np.arange(0, len(df)), df['SMA5'], label="5日均线")  # 绘制5日均线
        self.ax1.plot(np.arange(0, len(df)), df['SMA10'], label="10日均线")  # 绘制10日均线
        self.ax1.plot(np.arange(0, len(df)), df['SMA30'], label="30日均线")  # 绘制30日均线
        self.ax1.plot(np.arange(0, len(df)), df['SMA60'], label="60日均线")  # 绘制30日均线
        self.ax1.legend()

        red_pred = np.where(df["close"] > df["open"], df["volume"], 0)
        blue_pred = np.where(df["close"] < df["open"], df["volume"], 0)
        self.ax2.bar(np.arange(0, len(df)), red_pred, facecolor="red")
        self.ax2.bar(np.arange(0, len(df)), blue_pred, facecolor="blue")
        self.ax2.set(ylabel=u"成交量")

        low_list = df["close"].rolling(9, min_periods=1).min()
        high_list = df["high"].rolling(9, min_periods=1).max()
        rsv = (df["close"] - low_list) / (high_list - low_list) * 100
        df["K"] = rsv.ewm(com=2, adjust=False).mean()
        df["D"] = df["K"].ewm(com=2, adjust=False).mean()
        df["J"] = 3 * df["K"] - 2 * df["D"]
        self.ax3.plot(df["date"], df["K"], label="K")
        self.ax3.plot(df["date"], df["D"], label="D")
        self.ax3.plot(df["date"], df["J"], label="J")
        self.ax3.legend()
        self.ax3.set(ylabel=u"KDJ")

        EMA1 = df["close"].ewm(span=12, adjust=False).mean()
        EMA2 = df["close"].ewm(span=26, adjust=False).mean()
        DIF = EMA1 - EMA2
        DEA = DIF.ewm(span=9, adjust=False).mean()
        BAR = 2 * (DIF - DEA)

        red_bar = np.where(BAR > 0, BAR, 0)
        blue_bar = np.where(BAR < 0, BAR, 0)

        self.ax4.plot(np.arange(0, len(df)), DIF)
        self.ax4.plot(np.arange(0, len(df)), DEA)

        self.ax4.bar(np.arange(0, len(df)), red_bar, color="red")
        self.ax4.bar(np.arange(0, len(df)), blue_bar, color="blue")
        self.ax4.set(ylabel=u"MACD")
        self.ax1.xaxis.set_major_locator(ticker.MaxNLocator(9))

        def format_date(x, pos=None):
            if x < 0 or x > len(df['date']) - 1:
                return ''
            return df['date'][int(x)]

        self.ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
        self.ax1.grid(True)
        plt.setp(self.ax1.get_xticklabels(), visible=True)
        plt.setp(self.ax2.get_xticklabels(), visible=False)
        plt.setp(self.ax3.get_xticklabels(), visible=False)
        plt.setp(self.ax4.get_xticklabels(), visible=False)
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

class MyFrom(QMainWindow):
    # K线模块
    def init_kTab(self):
        self.grid_k = QGridLayout()
        self.grid_k.setSpacing(5)
        k_text = ['十字星', '两只乌鸦', '三只乌鸦', '三内部上涨和下跌', '三线打击',
                  '三外部上涨和下跌', '南方三星', '三个白兵', '弃婴', '大敌当前',
                  '捉腰带线', '脱离', '收盘缺影线', '藏婴吞没', '反击线'
            , '乌云压顶', '蜻蜓十字/T形十字', '吞噬模式', '十字暮星', '暮星',
                  '向上/下跳空并列阳线', '墓碑十字/倒T十字', '锤头', '上吊线', '母子线',
                  '十字孕线', '风高浪大线', '陷阱', '修正陷阱', '家鸽',
                  '三胞胎乌鸦', '颈内线', '倒锤头', '反冲形态', '由较长缺影线决定的反冲形态',
                  '停顿形态', '条形三明治', '探水竿', '跳空并列阴阳线', '插入',
                  '三星', '奇特三河床', '向上跳空的两只乌鸦', '上升/下降跳空三法']
        self.k_content = ['预示着当前趋势反转', '预示股价下跌', '预示股价下跌', '预示着股价上涨', '预示股价下跌',
                          '预示着股价上涨', '预示下跌趋势反转，股价上升', '预示股价上升', '预示趋势反转，发生在顶部下跌，底部上涨', '预示股价下跌'
            , '收盘价接近最高价，预示价格上涨', '预示价格上涨', '预示着趋势持续', '预示着底部反转', '预示趋势反转'
            , '预示着股价下跌', '预示趋势反转', '预示趋势反转', '预示顶部反转', '预示顶部反转',
                          '趋势持续', '预示底部反转', '处于下跌趋势底部,预示反转', '处于上升趋势的顶部，预示着趋势反转', '预示趋势反转，股价上升',
                          '预示着趋势反转', '预示着趋势反转', '趋势继续', '趋势继续', '预示着趋势反转',
                          '预示价格下跌', '预示着下跌继续', '在下跌趋势底部，预示着趋势反转', '存在跳空缺口', '与反冲形态类似，较长缺影线决定价格的涨跌',
                          '预示着上涨结束', '预示着股价上涨', '预示趋势反转', '上升趋势持续', '预示着趋势持续',
                          '预示着趋势反转', '收盘价不高于第二日收盘价，预示着反转，第二日下影线越长可能性越大', '预示股价下跌', '收盘价高于第一日收盘价，预示股价上升']
        self.K_method = ['CDLDOJISTAR', 'CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE',
                         'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 'CDLABANDONEDBABY', 'CDLADVANCEBLOCK',
                         'CDLBELTHOLD', 'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 'CDLCOUNTERATTACK',
                         'CDLDARKCLOUDCOVER', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 'CDLEVENINGDOJISTAR',
                         'CDLEVENINGSTAR',
                         'CDLGAPSIDESIDEWHITE', 'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN', 'CDLHARAMI',
                         'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON',
                         'CDLIDENTICAL3CROWS', 'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 'CDLKICKINGBYLENGTH',
                         'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING',
                         'CDLTRISTAR', 'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS']
        self.cb = QComboBox()
        self.cb.addItems(k_text)
        self.cb.currentIndexChanged.connect(self.selectionchange)
        self.cb_label = QLabel("预示着当前趋势反转")
        self.k_label = QLabel("选择K线图的形态：")
        self.grid_k.addWidget(self.k_label, 0, 0, 1, 1)
        self.grid_k.addWidget(self.cb, 0, 2, 1, 2)
        self.grid_k.addWidget(self.cb_label, 0, 5, 1, 5)
        self.kTab2.setLayout(self.grid_k)
        self.kLineThread = KLineThread()
        self.kLineThread.setValue("sh600690")
        self.kLineThread._signal.connect(self.kLineThread_callbacklog)
        self.kLineThread.start()

    def kLineThread_callbacklog(self, df):
        self.df = df
        self.mplK = KMplCanvas(self, width=5, height=4, dpi=100)
        self.mplK.start_staict_plot(df)
        mpl_ntb = NavigationToolbar(self.mplK, self)
        mpl_ntb.setStyleSheet("background-color:white;color:black")

        self.grid_k.addWidget(self.mplK, 2, 0, 13, 12)
        self.grid_k.addWidget(mpl_ntb, 2, 0, 1, 5)

    def selectionchange(self, i):
        self.cb_label.setText(self.k_content[i])
        self.mplK.start_staict_plot(self.df, self.K_method[i], i)

class KLineThread(QtCore.QThread):
    _signal = pyqtSignal(DataFrame)

    def __init__(self):
        super(KLineThread, self).__init__()

    def setValue(self, shareNumber):
        self.share_num = shareNumber

    def run(self):
        # df = pd.read_excel("海尔智家k.xlsx")
        df = 
        self._signal.emit(df)
