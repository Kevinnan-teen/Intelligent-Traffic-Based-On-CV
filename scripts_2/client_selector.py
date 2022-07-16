# -*- coding:utf-8 -*-
from main_window import Ui_MainWindow
from sub_window import App

import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2

from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QRegExp, Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
import threading
import multiprocessing
import time
import socket
import json
import selectors



class message(QThread):
    signal = pyqtSignal()
    def __init__(self, Window):
        super(message, self).__init__()
        self.window = Window
 
    def run(self):
        self.signal.emit()


class Main(QtWidgets.QMainWindow, Ui_MainWindow):

	logQueue = multiprocessing.Queue()		# 多进程队列，用于多进程之间传输数据

	subWinSignal = pyqtSignal(str)

	receiveLogSignal = pyqtSignal(str)

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.setupUi(self)
		self.cap = None
		# 设置窗口位于屏幕中心

		self.function_dict = {'target_detect_is_open':False, 'traffic_light_detect_is_open':False,
							  'cars_detect_is_open':False, 'people_detect_is_open':False, 
							  'license_plate_detect_is_open':False}
		
		self.keep_running = True

		self.rtmp_deal_address = ''

		# pyqt子线程中不能使用QmessageBox，使用信号与槽
		self.message = message(self)
		self.message.signal.connect(self.connectBox)
		
		# 窗口居中
		self.center()
		# 刷新视频流
		self.openFIleButton.clicked.connect(self.open_video)
	
		# 关闭视频
		self.closeFileButton.clicked.connect(self.close_video)

		# 获取rtmp流地址
		self.lineEdit.editingFinished.connect(self.rtmpTextchanged)
		self.rtmp_address = ''
		# 获取ip地址
		self.lineEdit_2.editingFinished.connect(self.ipAddressChanged)
		self.ip_address = ''
		# 获取端口地址
		self.lineEdit_3.editingFinished.connect(self.portChanged)
		self.port_address = ''

		# 创建一个关闭事件并设为未触发(清除视频线程)
		self.stopEvent = threading.Event()		
		self.stopEvent.clear()

		# 子窗口和父窗口通信
		self.sub_win = App()
		# 可视化数据
		self.lookVisualDataButton.clicked.connect(self.visualizeData)
		self.sub_data = ''
		self.subWinSignal.connect(lambda log2: self.sub_win.getData(log2))
		self.subWinThread = threading.Thread(target=self.subWinFunc, daemon=True)
		self.subWinThread.start()		

		# 加载日志
		self.receiveLogSignal.connect(lambda log: self.logOutput(log))
		self.logOutputThread = threading.Thread(target=self.receiveLog, daemon=True)
		self.logOutputThread.start()

		# Socket连接状态，如果连接则为True，如果断开则为False, 默认为断开	
		self.socket_state = False
		self.pushButton.clicked.connect(self.clickConnect)

		# 创建一个关闭事件并设为未触发(清除socket线程)
		self.stop_socket_event = threading.Event()
		self.stop_socket_event.clear()
		

	
	def connectBox(self):
	        load_completed = QMessageBox.information(self, 'message', '成功连接到服务器', QMessageBox.Ok)


	def clickConnect(self):
		if not self.socket_state:
			# 如果是之前是断开状态(close),则按钮显示是`connect`,需要将按钮改为`close`
			self.pushButton.setText("close")			
			self.client_tcp_thread = threading.Thread(target=self.connectServer, daemon=True)
			self.client_tcp_thread.start()
		else:
			# 如果之前是连接状态(connect),则按钮显示是`close`,需要将按钮改为`connect`
			#并且关闭socket
			print("set socket close")
			self.pushButton.setText("connect")
			self.stop_socket_event.set()
		self.socket_state = not self.socket_state		
		

	def visualizeData(self):
		self.sub_win.show()

	def subWinFunc(self):
		while True:
			time.sleep(0.2)			
			if self.sub_data != '':
				self.subWinSignal.emit(self.sub_data)

	def rtmpTextchanged(self):
		self.rtmp_address = str(self.lineEdit.text())
		self.rtmp_deal_address = self.rtmp_address
		print(self.lineEdit.text())


	def ipAddressChanged(self):
		self.ip_address = self.lineEdit_2.text()
		print(self.ip_address)

	def portChanged(self):
		self.port_address = self.lineEdit_3.text()
		print(self.port_address)



	def connectServer(self):
		self.logFile = open('../log/log_info.txt', 'a')
		while True:
			if self.ip_address != '' and self.port_address != '':
				break
			time.sleep(0.5)

		self.mysel = selectors.DefaultSelector()

		# 连接是一个阻塞操作， 因此在返回之后调用 setblocking() 方法
		server_address = (self.ip_address, int(self.port_address))
		print('connecting to {} port {}'.format(*server_address))
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		sock.connect(server_address)
		# 设置非阻塞
		sock.setblocking(False)

		# 设置选择器去监听 socket 是否可写的和是否可读
		self.mysel.register(
		    sock,
		    selectors.EVENT_READ | selectors.EVENT_WRITE,
		)


		#load_completed = QMessageBox.information(self, 'message', '成功连接到服务器', QMessageBox.Ok)
		if self.socket_state:
			self.message.start()
		
		# exit()

		origin_state = 0
		current_state = 0

		while True:
			time.sleep(0.5)
			# print(self.function_dict)	    
			# send_json = json.dumps(self.function_dict)
			#inp = pickle.dumps()		

			result_json = None
			result_dict = {}

			for key, mask in self.mysel.select(timeout=1):
			    connection = key.fileobj
			    client_address = connection.getpeername()
			    # print('client({})'.format(client_address))

			    if mask & selectors.EVENT_READ:
			        # print('  ready to read')
			        data = connection.recv(1024)
			        # print("if duse...")
			        if data:
			        	result_json = data.decode()
			        	result_dict = json.loads(result_json)
			        	# print(result_dict)
			            # A readable client socket has data
			            # print('receive:  ', data)
			            # bytes_received += len(data)

			    if mask & selectors.EVENT_WRITE:
			        # print('  ready to write')
			        # out = input('ready to write: ')
			        # print(out)
			        # print('  sending {!r}'.format(next_msg))
			        sock.sendall("server_data".encode())
			        # bytes_sent += len(next_msg)

			        # if out == "exit":
			        #     print("closing...")
			        #     self.keep_running = False
			if result_json == None:
				continue

			# 如果关闭连接
			if self.stop_socket_event.is_set():
				print("socket close")
				time.sleep(0.1)
				sock.sendall("exit".encode())
				self.stop_socket_event.clear()
				self.logFile.close()
				self.mysel.unregister(connection)
				connection.close()
				self.mysel.close()
				break
		
			# 目标检测
			if self.target_detect.isChecked():
				current_state = 1
				self.rtmp_deal_address = "rtmp://101.132.236.124/live/stream"

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
					pass
					self.rtmp_deal_address = self.rtmp_address

				self.green_light.setVisible(False)
				self.red_light.setVisible(False)
				self.break_traffic_label.setVisible(False)
				self.break_traffic_warning.setVisible(False)
				self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
				self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
				self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))

			if origin_state != current_state:
				# self.stopEvent.set()
				origin_state = current_state


			# 系统日志
			count_info_log = ''
			event_info_log = ''
			break_info_log = ''


			self.sub_data = str(result_dict['people_num']) + ' ' + str(result_dict['cars_num']) + \
						    ' ' + str(result_dict['motors_num'])

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

			if self.target_detect.isChecked():
					self.logQueue.put(self.log_info)
		print("socket finish")



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
		video_thread = threading.Thread(target=self.display_video, daemon=True)
		video_thread.start()
		


	def close_video(self):
		self.stopEvent.set()
		



	def display_video(self):		
		print("display")
		# "rtmp://kevinnan.org.cn/live/livestream"
		# "rtmp://kevinnan.org.cn/live/stream"

		while self.rtmp_deal_address[:4] != "rtmp":
			# print(self.rtmp_deal_address[:22])
			time.sleep(0.5)


		self.cap = cv2.VideoCapture(self.rtmp_deal_address)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 4)
		# self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
		self.openFIleButton.setEnabled(False)
		self.closeFileButton.setEnabled(True)

		self.FPS = 1 / int(self.cap.get(cv2.CAP_PROP_FPS))
		self.FPS_MS = int(self.FPS * 1000)

		print("display_2")
		while self.cap.isOpened():	
			#print("duse...1")
			ret, frame = self.cap.read()
			#print("duse....2")
			time.sleep(self.FPS)
			if ret:
				
				#frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
				# plate_frame = frame.copy()
				img = frame.copy()
				# print(img.shape)
				#output = None 
				#orign_img = None		

				#print("duse...3")					
		
				img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
				img = cv2.resize(img, (1080, 540)) 
				img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
				self.video_plate.setPixmap(QPixmap.fromImage(img))
				# cv2.waitKey(self.FPS_MS)
				# frames += 1 
				#print(frames)
				#print("duse...4")

				if self.stopEvent.is_set():
					self.stopEvent.clear()
					#self.textEdit.clear()
					self.video_plate.clear()
					# self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))
					# self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
					# self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
					break
				#print("duse....5")
			else:
				self.video_plate.clear()
				break
		try:
			self.openFIleButton.setEnabled(True)
			self.cap.release()
			#self.logFile.close()
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
