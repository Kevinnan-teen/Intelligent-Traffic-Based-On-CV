# -*- coding:utf-8 -*-
from core import Ui_MainWindow

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


		self.center()
		self.openFIleButton.clicked.connect(self.open_video)
		self.closeFileButton.clicked.connect(self.close_video)

		# 创建一个关闭事件并设为未触发
		self.stopEvent = threading.Event()		
		self.stopEvent.clear()


		# 加载模型
		self.load_models.clicked.connect(self.load_model)

		# 加载日志
		self.receiveLogSignal.connect(lambda log: self.logOutput(log))
		self.logOutputThread = threading.Thread(target=self.receiveLog, daemon=True)
		self.logOutputThread.start()

		#　调节帧率
		self.changeFrameSlider.valueChanged.connect(self.frameChange)
		self.frameInterval = self.changeFrameSlider.value()

		self.client_tcp_thread = threading.Thread(target=self.connectServer, daemon=True)
		self.client_tcp_thread.start()


	def connectServer(self):
		ip_port = ('127.0.0.1', 9996)

		s = socket.socket()     # 创建套接字

		s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)

		s.connect(ip_port)      # 连接服务器	


		while True:
			time.sleep(0.05)
			if self.target_detect.isChecked():
				self.function_dict['target_detect_is_open'] = True
			else:
				self.function_dict['target_detect_is_open'] = False
			if self.traffic_light_detect.isChecked():
				self.function_dict['traffic_light_detect_is_open'] = True
			else:
				self.function_dict['traffic_light_detect_is_open'] = False

			if self.cars_detect.isChecked():
				self.function_dict['cars_detect_is_open'] = True
			else:
				self.function_dict['cars_detect_is_open'] = False
			if self.people_detect.isChecked():
				self.function_dict['people_detect_is_open'] = True 
			else:
				self.function_dict['people_detect_is_open'] = False  
			if self.license_plate_detect.isChecked():
				self.function_dict['license_plate_detect_is_open'] = True
			else:
				self.function_dict['license_plate_detect_is_open'] = False

			# print(self.function_dict)	    
			send_json = json.dumps(self.function_dict)
			#inp = pickle.dumps()		    

			s.sendall(send_json.encode())

			# print("waiting recv...")

			result_json = s.recv(1024).decode()

			result_dict = json.loads(result_json)

			if(result_dict['data_h']):
				if(len(result_dict['plate_info_list'])):
					print(result_dict)
			# print(result_dict['data_h'])
			# if(result_dict['data_h'] != ''):
			# 	print(self.result_dict)



		s.close()       # 关闭连接


	def frameChange(self):
		self.label_14.setText(str(self.changeFrameSlider.value()))
		#print("frameInterval:" + str(self.frameInterval))


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
		self.logFile = open('../log/log_info.txt', 'a')


	def close_video(self):
		self.stopEvent.set()



	def display_video(self):
		print("display")
		file_name = "rtmp://kevinnan.org.cn/live/stream"
		self.cap = cv2.VideoCapture(file_name)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
		# self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
		self.openFIleButton.setEnabled(False)
		self.closeFileButton.setEnabled(True)

		self.FPS = int(self.cap.get(cv2.CAP_PROP_FPS))
		self.FPS_MS = int(self.FPS * 1000)

		frames = 0
		print("display")
		while self.cap.isOpened():
			print("display")
			ret, frame = self.cap.read()
			time.sleep(0.5)
			if ret:
				if frames % self.changeFrameSlider.value() == 0:
					#frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
					# plate_frame = frame.copy()
					img = frame.copy()
					output = None 
					orign_img = None

					# 系统日志
					count_info_log = ""
					event_info_log = ""
					break_info_log = ""
		

					log_info = count_info_log + event_info_log + break_info_log
					self.logQueue.put(log_info)			
					
									
			
					img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
					img = cv2.resize(img, (1080, 540)) 
					img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
					self.video_plate.setPixmap(QPixmap.fromImage(img))
				# cv2.waitKey(self.FPS_MS)
				frames += 1 
				#print(frames)

				if self.stopEvent.is_set():
					self.stopEvent.clear()
					#self.textEdit.clear()
					self.video_plate.clear()
					self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))
					self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
					self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
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
		


	def load_model(self):
		CUDA = torch.cuda.is_available() 
		print("Loading network.....")
		self.model = Darknet("../yolov3/cfg/yolov3.cfg")
		#self.model = Darknet("../yolov3/cfg/yolov2-tiny.cfg")
		self.model.load_weights("../yolov3/weights/yolov3.weights")
		#self.model.load_weights("../yolov3/weights/yolov2-tiny.weights")

		print("Network successfully loaded")
		self.model.net_info["height"] = 416
		inp_dim = int(self.model.net_info["height"])
		assert inp_dim % 32 == 0 
		assert inp_dim > 32

		if CUDA:
		    self.model.cuda()                        # 将模型迁移到GPU
		self.model.eval()

		load_completed = QMessageBox.information(self, 'message', '模型加载完成．', QMessageBox.Ok)
		#load_completed.setText();
		#load_completed.exec()




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Main()
    window.show()
    sys.exit(app.exec_())