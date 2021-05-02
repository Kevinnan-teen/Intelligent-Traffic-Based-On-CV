import numpy as np
import sys
import matplotlib
matplotlib.use('Qt5Agg')
import matplotlib.pyplot as plt
from pylab import *

# 使用 matplotlib中的FigureCanvas (在使用 Qt5 Backends中 FigureCanvas继承自QtWidgets.QWidget)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import QTimer
import sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QRect


class App(QWidget):
    def __init__(self, parent=None):
        # 父类初始化方法
        super(App, self).__init__(parent)
        self.initUI()
        self.center()

    def initUI(self):
        self.setWindowTitle('数据可视化')
        self.setFixedSize(800, 600)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(800, 600)
        # 几个QWidgets
  
        self.startBtn = QPushButton('开始')
        self.endBtn = QPushButton('结束')
        self.startBtn.clicked.connect(self.startTimer)
        self.endBtn.clicked.connect(self.endTimer)
        # 时间模块
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.showTime)
        #图像模块
        self.figure = plt.figure()

        self.canvas = FigureCanvas(self.figure)
        #垂直布局

        layout=QVBoxLayout()
        layout.addWidget(self.startBtn)
        layout.addWidget(self.endBtn)
        layout.addWidget( self.canvas )
        self.setLayout(layout)

        # 数组初始化
        self.people_num_list=[]
        self.cars_num_list = []
        self.motors_num_list = []

    def center(self,screenNum=0):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.normalGeometry2= QRect((screen.width()-size.width())/2+screen.left(),
                    (screen.height()-size.height())/2,
                    size.width(),size.height())
        self.setGeometry((screen.width()-size.width())/2+screen.left(),
                        (screen.height()-size.height())/2,
                        size.width(),size.height())


    def showTime(self):
        #shuju=np.random.random_sample()*10#返回一个[0,1)之间的浮点型随机数*10
        #shuju_2=np.random.random_sample()*10#返回一个[0,1)之间的浮点型随机数*10
        #self.x.append(shuju)#数组更新
        #self.xx.append(shuju_2)
        ax = self.figure.add_axes([0.1, 0.1, 0.8, 0.8])

        ax.clear()
        ax.plot(self.people_num_list, label="people_num", linewidth=2, color="g")
        ax.plot(self.cars_num_list, label="cars_num", color="b")
        ax.plot(self.motors_num_list, label="motors_num", color="r")

        self.figure.legend()
        self.canvas.draw()
        plt.grid(True)
    # 启动函数
    def startTimer(self):
        # 设置计时间隔并启动
        self.timer.start(100)#每隔一秒执行一次绘图函数 showTime
        self.startBtn.setEnabled(False)#开始按钮变为禁用
        self.endBtn.setEnabled(True)#结束按钮变为可用
    def endTimer(self):
        self.timer.stop()#计时停止
        self.startBtn.setEnabled(True)#开始按钮变为可用
        self.endBtn.setEnabled(False)#结束按钮变为可用
        self.people_num_list = []
        self.cars_num_list = []
        self.motors_num_list = []
        

    def getData(self, data):        
        data_list = str(data).split(' ')
        people_num = int(float(data_list[0]))
        cars_num = int(float(data_list[1]))
        motors_num = int(float(data_list[2]))
        # print(people_num, cars_num, motors_num)
        self.people_num_list.append(people_num)
        self.cars_num_list.append(cars_num)
        self.motors_num_list.append(motors_num)



