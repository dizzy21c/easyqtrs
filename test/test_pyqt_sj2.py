import sys, traceback
# reload(sys)
# sys.setdefaultencoding('utf-8')
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
import pyqtgraph as pg
import tushare as ts
import numpy as np

# 主窗口类
class MainUi(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("州的先生zmister.com A股股票历史走势K线图")
        self.main_widget = QtWidgets.QWidget() # 创建一个主部件
        self.main_layout = QtWidgets.QGridLayout() # 创建一个网格布局
        self.main_widget.setLayout(self.main_layout) # 设置主部件的布局为网格
        self.setCentralWidget(self.main_widget) # 设置窗口默认部件

        self.stock_code = QtWidgets.QLineEdit() # 创建一个文本输入框部件
        self.option_sel = QtWidgets.QComboBox() # 创建一个下拉框部件
        # self.option_sel.addItem("近7天")
        # self.option_sel.addItem("近30天")
        self.option_sel.addItem("近60天")
        self.option_sel.addItem("近180天")
        self.option_sel.addItem("近360天")
        self.que_btn = QtWidgets.QPushButton("查询") # 创建一个按钮部件
        self.k_widget = QtWidgets.QWidget() # 实例化一个widget部件作为K线图部件
        self.k_layout = QtWidgets.QGridLayout() # 实例化一个网格布局层
        self.k_widget.setLayout(self.k_layout) # 设置K线图部件的布局层
        self.k_plt = pg.PlotWidget() # 实例化一个绘图部件
        self.k_layout.addWidget(self.k_plt) # 添加绘图部件到K线图部件的网格布局层

        # 将上述部件添加到布局层中
        self.main_layout.addWidget(self.stock_code,0,0,1,1)
        self.main_layout.addWidget(self.option_sel,0,1,1,1)
        self.main_layout.addWidget(self.que_btn,0,2,1,1)
        self.main_layout.addWidget(self.k_widget,1,0,3,3)

        self.que_btn.clicked.connect(self.query_slot) # 绑定按钮点击信号
        self.move_slot = pg.SignalProxy(self.k_plt.scene().sigMouseMoved, rateLimit=60, slot=self.print_slot)

    def plot_k_line(self,code=None,start=None,end=None):
        self.data = ts.get_hist_data(code=code, start=start, end=end).sort_index()
        
        self.xdict = dict(enumerate(self.data.index))
        # self.xdict = list(self.xdict.keys())
        self.xdict = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 3)]
        self.xdict = np.asarray(self.xdict)
        
        y_min = self.data['low'].min()
        y_max = self.data['high'].max()
        data_list = []
        d = 0
        for dates, row in self.data.iterrows():
            # 将时间转换为数字
            date_time = datetime.datetime.strptime(dates, '%Y-%m-%d')
            # t = date2num(date_time)
            open, high, close, low = row[:4]
            datas = (d, open, close, low, high)
            data_list.append(datas)
            print(datas)
            d += 1
        self.axis_dict = dict(enumerate(self.data.index))
        # 州的先生 zmister.com
        axis_1 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 3)]  # 获取日期值
        axis_2 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 5)]
        axis_3 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 8)]
        axis_4 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 10)]
        axis_5 = [(i, list(self.data.index)[i]) for i in range(0, len(self.data.index), 30)]
        stringaxis = pg.AxisItem(orientation='bottom')  # 创建一个刻度项
        stringaxis.setTicks([axis_5, axis_4, axis_3, axis_2, axis_1, self.axis_dict.items()])  # 设置X轴刻度值
        self.k_plt.getAxis("bottom").setTicks([axis_5, axis_4, axis_3, axis_2, axis_1, self.axis_dict.items()])

        self.k_plt.plotItem.clear() # 清空绘图部件中的项
        item = CandlestickItem(data_list)  # 生成蜡烛图数据
        self.k_plt.addItem(item, )  # 在绘图部件中添加蜡烛图项目
        self.k_plt.showGrid(x=True, y=True)  # 设置绘图部件显示网格线
        self.k_plt.setYRange(y_min,y_max)
        self.k_plt.setLabel(axis='left', text='指数')  # 设置Y轴标签
        self.k_plt.setLabel(axis='bottom', text='日期')  # 设置X轴标签
        self.label = pg.TextItem()  # 创建一个文本项
        self.k_plt.addItem(self.label)  # 在图形部件中添加文本项

        self.k_plt.plot(x=self.xdict, y=self.data['close'].values, pen='g', name='收盘指数',symbolBrush=(0,255,0))

        self.vLine = pg.InfiniteLine(angle=90, movable=False, )  # 创建一个垂直线条
        self.hLine = pg.InfiniteLine(angle=0, movable=False, )  # 创建一个水平线条
        self.k_plt.addItem(self.vLine, ignoreBounds=True)  # 在图形部件中添加垂直线条
        self.k_plt.addItem(self.hLine, ignoreBounds=True)  # 在图形部件中添加水平线条

    # 查询按钮信号槽
    def query_slot(self):
        try:
            self.que_btn.setEnabled(False)
            self.que_btn.setText("查询中…")
            code = self.stock_code.text()
            date_sel = self.option_sel.currentText()[1:-1]
            start_date = datetime.datetime.today()-datetime.timedelta(days=int(date_sel)+1)
            start_date_str = datetime.datetime.strftime(start_date,"%Y-%m-%d")
            end_date = datetime.datetime.today()-datetime.timedelta(days=1)
            end_date_str = datetime.datetime.strftime(end_date,"%Y-%m-%d")
            print(code,start_date_str,end_date_str)
            self.plot_k_line(code=code,start=start_date_str,end=end_date_str)
            self.que_btn.setEnabled(True)
            self.que_btn.setText("查询")
        except Exception as e:
            print(traceback.print_exc())

    # 响应鼠标移动绘制十字光标
    def print_slot(self, event=None):
        if event is None:
            print("事件为空")
        else:
            pos = event[0]  # 获取事件的鼠标位置
            try:
                # 如果鼠标位置在绘图部件中
                if self.k_plt.sceneBoundingRect().contains(pos):
                    mousePoint = self.k_plt.plotItem.vb.mapSceneToView(pos)  # 转换鼠标坐标
                    index = int(mousePoint.x())  # 鼠标所处的X轴坐标
                    pos_y = int(mousePoint.y())  # 鼠标所处的Y轴坐标
                    if -1 < index < len(self.data.index):
                        # 在label中写入HTML
                        self.label.setHtml(
                            "<p style='color:white'><strong>日期：{0}</strong></p><p style='color:white'>开盘：{1}</p><p style='color:white'>收盘：{2}</p><p style='color:white'>最高价：<span style='color:red;'>{3}</span></p><p style='color:white'>最低价：<span style='color:green;'>{4}</span></p>".format(
                                self.axis_dict[index], self.data['open'][index], self.data['close'][index],
                                self.data['high'][index], self.data['low'][index]))
                        self.label.setPos(mousePoint.x(), mousePoint.y())  # 设置label的位置
                    # 设置垂直线条和水平线条的位置组成十字光标
                    self.vLine.setPos(mousePoint.x())
                    self.hLine.setPos(mousePoint.y())
            except Exception as e:
                print(traceback.print_exc())

# K线图绘制类
class CandlestickItem(pg.GraphicsObject):
    # 州的先生zmister.com
    def __init__(self, data):
        pg.GraphicsObject.__init__(self)
        self.data = data  # data里面必须有以下字段: 时间, 开盘价, 收盘价, 最低价, 最高价
        self.generatePicture()

    def generatePicture(self):
        self.picture = QtGui.QPicture() # 实例化一个绘图设备
        p = QtGui.QPainter(self.picture) # 在picture上实例化QPainter用于绘图
        p.setPen(pg.mkPen('w')) # 设置画笔颜色
        w = (self.data[1][0] - self.data[0][0]) / 3.
        for (t, open, close, min, max) in self.data:
            print(t, open, close, min, max)
            p.drawLine(QtCore.QPointF(t, min), QtCore.QPointF(t, max)) # 绘制线条
            if open > close: # 开盘价大于收盘价
                p.setBrush(pg.mkBrush('g')) # 设置画刷颜色为绿
            else:
                p.setBrush(pg.mkBrush('r')) # 设置画刷颜色为红
            p.drawRect(QtCore.QRectF(t - w, open, w * 2, close - open)) # 绘制箱子
        p.end()

    def paint(self, p, *args):
        p.drawPicture(0, 0, self.picture)

    def boundingRect(self):
        return QtCore.QRectF(self.picture.boundingRect())


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    # MainWindow = QtGui.QMainWindow()
    ui = MainUi()
    # ui.setupUi(MainWindow)
    # MainWindow.show()
    ui.show()
    sys.exit(app.exec_())
