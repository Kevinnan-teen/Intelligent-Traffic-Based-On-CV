import sys
import matplotlib
matplotlib.use("Qt5Agg") # 声明使用pyqt5
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg # pyqt5的画布
import matplotlib.pyplot as plt
from matplotlib.figure import Figure 
from matplotlib.animation import FuncAnimation
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow
from PyQt5 import QtWidgets,QtCore
import numpy as np

import time
import threading

class MyMatplotlibFigure(FigureCanvasQTAgg):
    """
    创建一个画布类，并把画布放到FigureCanvasQTAgg
    """
    def __init__(self, width=10, heigh=10, dpi=100):
        plt.rcParams['figure.facecolor'] = 'r'  # 设置窗体颜色
        plt.rcParams['axes.facecolor'] = 'b'  # 设置绘图区颜色
        # 创建一个Figure,该Figure为matplotlib下的Figure，不是matplotlib.pyplot下面的Figure
        self.figs = Figure(figsize=(width, heigh), dpi=dpi)
        super(MyMatplotlibFigure, self).__init__(self.figs)  # 在父类种激活self.fig， 
        self.axes = self.figs.add_subplot(111)  # 添加绘图区
    def mat_plot_drow_axes(self, t, s):
        """
        用清除画布刷新的方法绘图
        :return:
        """
        self.axes.clear()
        self.figs.canvas.draw_idle()
        # self.axes.cla()  # 清除绘图区


        self.axes.spines['top'].set_visible(False)  # 顶边界不可见
        self.axes.spines['right'].set_visible(False)  # 右边界不可见
        # 设置左、下边界在（0，0）处相交
        # self.axes.spines['bottom'].set_position(('data', 0))  # 设置y轴线原点数据为 0
        self.axes.spines['left'].set_position(('data', 0))  # 设置x轴线原点数据为 0
        self.axes.plot(t, s, 'o-r', linewidth=0.5)
        self.figs.canvas.draw()  # 这里注意是画布重绘，self.figs.canvas
        self.figs.canvas.flush_events()  # 画布刷新self.figs.canvas

class MainDialogImgBW(QtWidgets.QMainWindow):
    """
    创建UI主窗口，使用画板类绘图。
    """
    def __init__(self):
        super(MainDialogImgBW, self).__init__()
        self.multiple_change_thread = threading.Thread(target=self.multiple_change, daemon=True)
        self.multiple_change_thread.start()

        self.setWindowTitle("显示matplotlib")
        self.setObjectName("widget")
        self.resize(800, 600)
        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(0, 0, 800, 600))
        self.canvas = MyMatplotlibFigure(width=5, heigh=4, dpi=100)
        self.plotcos()
        self.hboxlayout = QtWidgets.QHBoxLayout(self.label)
        self.hboxlayout.addWidget(self.canvas)

    def plotcos(self):
        # plt.clf()

        t = np.arange(0.0, 5.0, 0.1)
        s = self.mm * np.cos(2 * np.pi * t)
        self.canvas.mat_plot_drow_axes(t, s)
        self.canvas.figs.suptitle("sin")  # 设置标题
        print(s)


    def multiple_change(self):    
        i = 0
        while True:

            self.mm = 1 + i
            i += 0.2

            time.sleep(1)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main = MainDialogImgBW()
    main.show()
    sys.exit(app.exec_())