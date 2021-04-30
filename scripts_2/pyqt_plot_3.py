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

class MyMatPlotAnimation(FigureCanvasQTAgg):
  """
  创建一个画板类，并把画布放到容器（画板上）FigureCanvasQTAgg，再创建一个画图区
  """
  def __init__(self, width=10, heigh=10, dpi=100):
    # 创建一个Figure,该Figure为matplotlib下的Figure，不是matplotlib.pyplot下面的Figure
    self.figs = Figure(figsize=(width, heigh), dpi=dpi)
    super(MyMatPlotAnimation, self).__init__(self.figs) 
    self.figs.patch.set_facecolor('#01386a') # 设置绘图区域颜色
    self.axes = self.figs.add_subplot(111)

  def set_mat_func(self, t, s):
    """
    初始化设置函数
    """
    self.t = t
    self.s = s
    self.axes.cla()
    self.axes.patch.set_facecolor("#000000") # 设置ax区域背景颜色
    self.axes.patch.set_alpha(0.5) # 设置ax区域背景颜色透明度

    # self.axes.spines['top'].set_color('#01386a')
    self.axes.spines['top'].set_visible(False) # 顶边界不可见
    self.axes.spines['right'].set_visible(False) # 右边界不可见

    self.axes.xaxis.set_ticks_position('bottom') # 设置ticks（刻度）的位置为下方
    self.axes.yaxis.set_ticks_position('left') # 设置ticks（刻度） 的位置为左侧
    # 设置左、下边界在（0，0）处相交
    # self.axes.spines['bottom'].set_position(('data', 0)) # 设置x轴线再Y轴0位置
    self.axes.spines['left'].set_position(('data', 0)) # 设置y轴在x轴0位置
    self.plot_line, = self.axes.plot([], [], 'r-', linewidth=1) # 注意‘,'不可省略
    
  def plot_tick(self):
    plot_line = self.plot_line
    plot_axes = self.axes
    t = self.t
    
    def upgrade(i): # 注意这里是plot_tick方法内的嵌套函数
      x_data = [] # 这里注意如果是使用全局变量self定义，可能会导致绘图首位相联
      y_data = []
      for i in range(len(t)):
        x_data.append(i)
        y_data.append(self.s[i])
      plot_axes.plot(x_data, y_data, 'r-', linewidth=1)
      return plot_line, # 这里也是注意‘,'不可省略，否则会报错
      
    ani = FuncAnimation(self.figs, upgrade, blit=True, repeat=False)
    self.figs.canvas.draw() # 重绘还是必须要的


class MainDialogImgBW(QtWidgets.QMainWindow):
  def __init__(self):
    super(MainDialogImgBW, self).__init__()

    self.setWindowTitle("显示matplotlib")
    self.setObjectName("widget")
    self.resize(800, 600)
    self.label = QtWidgets.QLabel(self)
    self.label.setGeometry(QtCore.QRect(60, 100, 300, 200))
    self.canvas = MyMatPlotAnimation(width=5, heigh=4, dpi=100)
    self.plotcos()
    self.hboxlayout = QtWidgets.QHBoxLayout(self.label)
    self.hboxlayout.addWidget(self.canvas)

    

  def plotcos(self):
    t = np.arange(0.0, 5.0, 0.1)
    s = self.mm * np.cos(2 * np.pi * t)
    print(s)
    self.canvas.set_mat_func(t, s)
    self.canvas.plot_tick()




if __name__ == "__main__":
  app = QtWidgets.QApplication(sys.argv)
  main = MainDialogImgBW()
  main.show()
  sys.exit(app.exec_())