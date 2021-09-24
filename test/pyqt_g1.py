import pyqtgraph as pg

class CandlestickItem(pg.GraphicsObject):  
    def __init__(self, data):  
        pg.GraphicsObject.**init**(self)  
        self.data = data ## data must have fields: time, open, close, min, max  
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture()
        p = QtGui.QPainter(self.picture)
        p.setPen(pg.mkPen('w'))
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max))
            if open > close:
                p.setBrush(pg.mkBrush('g'))
            else:
                p.setBrush(pg.mkBrush('r'))
            p.drawRect(QtCore.QRectF(t-w, open, w*2, close-open))
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())

def chart():
    hist_data = ts.get_hist_data('600519',start='2017-05-01',end='2017-11-24')
    data_list = []
    axis = []
    for dates,row in hist_data.iterrows():
        # 将时间转换为数字
        date_time = datetime.datetime.strptime(dates,'%Y-%m-%d')
        t = date2num(date_time)
        # t = dict(enumerate(datetime))
        open,high,close,low = row[:4]
        datas = (t,open,close,low,high)
        data_list.append(datas)
        axis.append(t)
    # print(axis)
    axis_dict = dict(enumerate(axis))
    item = CandlestickItem(data_list)
    plt = pg.PlotWidget()
    # print(plt.getAxis('bottom'))
    plt.addItem(item)
    plt.showGrid(x=True,y=True)
    return plt

class MainWindow(object):  
    def __init__(self):  
        self.ui.verticalLayout_3.addWidget(chart())  