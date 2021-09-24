# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'QWidget_plot.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')
from PyQt5 import QtCore, QtGui
import datetime
import pyqtgraph as pg
import tushare as ts

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout"))
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        MainWindow.setMenuBar(self.menubar)

        self.drawChart = DrawChart(ktype='D')
        self.verticalLayout_2.addWidget(self.drawChart.pyqtgraphDrawChart())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))


class DrawChart():
    def __init__(self, code='sz50', start=str(datetime.date.today() - datetime.timedelta(days=200)), end=str(datetime.date.today() + datetime.timedelta(days=1)), ktype='D'):
        self.code = code
        self.start = start
        self.end = end
        self.ktype = ktype
        self.data_list, self.t = self.getData()

    def pyqtgraphDrawChart(self):
        try:
            self.item = CandlestickItem(self.data_list)
            self.xdict = {0: str(self.hist_data.index[0]).replace('-', '/'), int((self.t + 1) / 2) - 1: str(self.hist_data.index[int((self.t + 1) / 2)]).replace('-', '/'), self.t - 1: str(self.hist_data.index[-1]).replace('-', '/')}
            self.stringaxis = pg.AxisItem(orientation='bottom')
            self.stringaxis.setTicks([self.xdict.items()])
            self.plt = pg.PlotWidget(axisItems={'bottom': self.stringaxis}, enableMenu=False)

            self.plt.addItem(self.item)
            # self.plt.showGrid(x=True, y=True)

            return self.plt
        except:
            return pg.PlotWidget()

    def getData(self):
        self.start = str(datetime.date.today() - datetime.timedelta(days=150))
        self.end = str(datetime.date.today() + datetime.timedelta(days=1))
        self.hist_data = ts.get_hist_data(self.code, self.start, self.end, self.ktype).sort_index()[-300:-1]
        data_list = []
        t = 0
        for dates, row in self.hist_data.iterrows():
            open, high, close, low, volume, price_change, p_change, ma5, ma10, ma20 = row[:10]
            datas = (t, open, close, low, high, volume, price_change, p_change, ma5, ma10, ma20)
            data_list.append(datas)
            t += 1
        return data_list, t


class CandlestickItem(pg.GraphicsObject):
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        prema5 = 0
        prema10 = 0
        prema20 = 0
        for (t, open, close, min, max, volume, price_change, p_change, ma5, ma10, ma20) in self.data:
            if open > close:
                p.setPen(pg.mkPen('g'))
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setPen(pg.mkPen('r'))
                p.setBrush(pg.mkBrush('r'))
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open))
            if prema5 != 0:
                p.setPen(pg.mkPen('w'))
                p.setBrush(pg.mkBrush('w'))
                p.drawLine(QtCore.QPointF(t-1, prema5), QtCore.QPointF(t, ma5))
            prema5 = ma5
            if prema10 != 0:
                p.setPen(pg.mkPen('c'))
                p.setBrush(pg.mkBrush('c'))
                p.drawLine(QtCore.QPointF(t-1, prema10), QtCore.QPointF(t, ma10))
            prema10 = ma10
            if prema20 != 0:
                p.setPen(pg.mkPen('m'))
                p.setBrush(pg.mkBrush('m'))
                p.drawLine(QtCore.QPointF(t-1, prema20), QtCore.QPointF(t, ma20))
            prema20 = ma20
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())



if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
