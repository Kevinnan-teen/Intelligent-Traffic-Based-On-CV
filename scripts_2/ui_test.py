# -*- coding:utf-8 -*-
from core_2 import Ui_MainWindow
from pyqt_plot_6 import App

import sys
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2

from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QRegExp, Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
import threading
import torch
import multiprocessing
import time
import socket
import json




class Main(QtWidgets.QMainWindow, Ui_MainWindow):

	logQueue = multiprocessing.Queue()		# 多进程队列，用于多进程之间传输数据

	receiveLogSignal = pyqtSignal(str)

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.setupUi(self)
		self.cap = None
		# 设置窗口位于屏幕中心

		self.function_dict = {'target_detect_is_open':False, 'traffic_light_detect_is_open':False,
							  'cars_detect_is_open':False, 'people_detect_is_open':False, 
							  'license_plate_detect_is_open':False}

		self.rtmp_deal_address = ''

		self.center()
		self.openFIleButton.clicked.connect(self.open_video)

		self.sub_win = App()
		# window.closeFileButton.clicked.connect(sub_win.show)

		#sub_win = App()
		#self.closeFileButton.clicked.connect(sub_win.show)

		self.closeFileButton.clicked.connect(self.close_video)

		# 获取rtmp流地址
		self.lineEdit.editingFinished.connect(self.rtmpTextchanged)
		self.rtmp_address = ''

		# 创建一个关闭事件并设为未触发
		self.stopEvent = threading.Event()		
		self.stopEvent.clear()

	

		# 加载日志
		self.receiveLogSignal.connect(lambda log: self.logOutput(log))
		self.logOutputThread = threading.Thread(target=self.receiveLog, daemon=True)
		self.logOutputThread.start()

		

		self.client_tcp_thread = threading.Thread(target=self.connectServer, daemon=True)
		self.client_tcp_thread.start()


	def rtmpTextchanged(self):
		self.rtmp_address = self.lineEdit.text()
		print(self.lineEdit.text())



	def connectServer(self):
		ip_port = ('127.0.0.1', 9996)

		s = socket.socket()     # 创建套接字

		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

		s.connect(ip_port)      # 连接服务器	

		origin_state = 0
		current_state = 0

		while True:
			time.sleep(0.05)
			# print(self.function_dict)	    
			# send_json = json.dumps(self.function_dict)
			#inp = pickle.dumps()		    

			s.sendall("server_data".encode())

			# print("waiting recv...")

			result_json = s.recv(1024).decode()

			result_dict = json.loads(result_json)

			# if(result_dict['data_h']):
			# 	if(len(result_dict['plate_info_list'])):
			# 		print(result_dict)

		
			# 目标检测
			if self.target_detect.isChecked():
				current_state = 1
				self.rtmp_deal_address = "rtmp://kevinnan.org.cn/live/stream"

				# 交通灯检测
				if self.traffic_light_detect.isChecked():
					if result_dict['traffic_light_color'] == "green":
						self.red_light.setVisible(False)
						self.green_light.setVisible(True)
					elif result_dict['traffic_light_color'] == "red":
						self.green_light.setVisible(False)
						self.red_light.setVisible(True)
					else:
						self.green_light.setVisible(False)
						self.red_light.setVisible(False)
				else:
					self.green_light.setVisible(False)
					self.red_light.setVisible(False)
				# 车流量检测
				if self.cars_detect.isChecked():	
					# print("cars_detect")	
					self.tableWidget.setItem(0,1,QTableWidgetItem(str(result_dict['cars_num'])))
					self.tableWidget.setItem(0,2,QTableWidgetItem(str(result_dict['motors_num'])))
				else:
					self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
					self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
				# 人流量检测
				if self.people_detect.isChecked():	
					# print("people_detect")			
					self.tableWidget.setItem(0,0,QTableWidgetItem(str(result_dict['people_num'])))
				else:
					self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))
				# 车牌检测
				if self.license_plate_detect.isChecked():
					pass
				else:
					self.license_graph.clear()
					self.license_result.clear()

			else:
				current_state = 0
				if self.rtmp_address != '':
					self.rtmp_deal_address = self.rtmp_address

				self.green_light.setVisible(False)
				self.red_light.setVisible(False)
				self.break_traffic_label.setVisible(False)
				self.break_traffic_warning.setVisible(False)
				self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
				self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
				self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))

			if origin_state != current_state:
				self.stopEvent.set()
				origin_state = current_state


			# 系统日志
			count_info_log = ''
			event_info_log = ''
			break_info_log = ''

			count_info_log = "people:" + str(result_dict['people_num']) + ", cars:" + str(result_dict['cars_num']) + \
										", motors:" + str(result_dict['motors_num']) + ";\n"

			plate_info_list = result_dict['plate_info_list']

			if len(plate_info_list):
				event_info_log = "车牌信息：" + plate_info_list[0][0] + \
								 "识别准确率:" + str(plate_info_list[0][1])[:5] + '\n'
			if(result_dict['pedestrians_num']):
				break_info_log = str(result_dict['pedestrians_num']) + "人闯红灯;\n"
				self.break_traffic_warning.setVisible(True)
				self.break_traffic_label.setVisible(True)
				self.break_traffic_label.setText(break_info_log)
			else:
				self.break_traffic_label.setVisible(False)
				self.break_traffic_warning.setVisible(False)
			

			self.log_info = count_info_log + event_info_log + break_info_log
			
			
		s.close()       # 关闭连接



	def logOutput(self, log):
		# 获取当前系统时间
		time = datetime.now().strftime('[%Y/%m/%d %H:%M:%S]')
		log = time + '\n' + log 
		# 写入日志文件
		self.logFile.write(log)
		#　界面日志打印
		self.textEdit.moveCursor(QTextCursor.End)
		self.textEdit.insertPlainText(log)
		self.textEdit.ensureCursorVisible()  # 自动滚屏

	def receiveLog(self):
		while True:
			data = self.logQueue.get()
			if data:
				self.receiveLogSignal.emit(data)
			else:
				continue


	def center(self,screenNum=0):
		screen = QDesktopWidget().screenGeometry()
		size = self.geometry()
		self.normalGeometry2= QRect((screen.width()-size.width())/2+screen.left(),
					(screen.height()-size.height())/2,
					size.width(),size.height())
		self.setGeometry((screen.width()-size.width())/2+screen.left(),
						(screen.height()-size.height())/2,
						size.width(),size.height())

	def open_video(self):
		video_thread = threading.Thread(target=self.display_video)
		video_thread.start()
		


	def close_video(self):
		# self.stopEvent.set()
		self.sub_win.show()



	def display_video(self):
		self.logFile = open('../log/log_info.txt', 'a')
		print("display")
		# "rtmp://kevinnan.org.cn/live/livestream"
		# "rtmp://kevinnan.org.cn/live/stream"

		while self.rtmp_deal_address[:22] != "rtmp://kevinnan.org.cn":
			time.sleep(0.1)

		self.cap = cv2.VideoCapture(self.rtmp_deal_address)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
		# self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
		self.openFIleButton.setEnabled(False)
		self.closeFileButton.setEnabled(True)

		self.FPS = 1 / int(self.cap.get(cv2.CAP_PROP_FPS))
		self.FPS_MS = int(self.FPS * 1000)

		print("display_2")
		while self.cap.isOpened():	
			ret, frame = self.cap.read()
			time.sleep(self.FPS)
			if ret:
				
				#frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
				# plate_frame = frame.copy()
				img = frame.copy()
				output = None 
				orign_img = None		
				
				if self.target_detect.isChecked():
					self.logQueue.put(self.log_info)					
		
				img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
				img = cv2.resize(img, (1080, 540)) 
				img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
				self.video_plate.setPixmap(QPixmap.fromImage(img))
				# cv2.waitKey(self.FPS_MS)
				# frames += 1 
				#print(frames)

				if self.stopEvent.is_set():
					self.stopEvent.clear()
					#self.textEdit.clear()
					self.video_plate.clear()
					# self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))
					# self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
					# self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
					break
			else:
				self.video_plate.clear()
				break
		try:
			self.openFIleButton.setEnabled(True)
			self.cap.release()
			self.logFile.close()
			self.green_light.setVisible(False)
			self.red_light.setVisible(False)
			self.break_traffic_warning.setVisible(False)
			self.break_traffic_label.setVisible(False)
			self.license_graph.clear()
			self.license_result.clear()
		except:
			print("资源释放错误")
		



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()


    sys.exit(app.exec_())