from core import Ui_MainWindow
from video_demo import target_detect, traffic_light_detect, classNum_detect
from darknet import Darknet
from plateRecognition import recognize_plate, drawRectBox
from detect import detect_car_color


import sys
#sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
from datetime import datetime
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, QRegExp, Qt, QRect
from PyQt5.QtGui import QImage, QPixmap, QTextCursor
import cv2
import threading
import torch
import multiprocessing




class Main(QtWidgets.QMainWindow, Ui_MainWindow):

	logQueue = multiprocessing.Queue()		# 多进程队列，用于多进程之间传输数据
	receiveLogSignal = pyqtSignal(str)

	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)
		self.setupUi(self)
		self.cap = None
		# 设置窗口位于屏幕中心
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
		fileName,_ = QFileDialog.getOpenFileName(self, "载入监控视频",'../videos')
		# fileName = "rtmp://kevinnan.org.cn/live/livestream"
		self.cap = cv2.VideoCapture(fileName)
		self.frameRate = self.cap.get(cv2.CAP_PROP_FPS)
		#self.frameRate = self.cap.get(cv2.CAP_PROP_BUFFERSIZE)
		self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)
		video_thread = threading.Thread(target=self.display_video)
		video_thread.start()
		self.logFile = open('../log/log_info.txt', 'a')


	def close_video(self):
		self.stopEvent.set()



	def display_video(self):
		self.openFIleButton.setEnabled(False)
		self.closeFileButton.setEnabled(True)
        # RGB转BGR
		frames = 0
		while self.cap.isOpened():
			ret, frame = self.cap.read()
			if ret:
				if frames % self.changeFrameSlider.value() == 0:
					#frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
					plate_frame = frame.copy()
					img = frame.copy()
					output = None 
					orign_img = None

					# 系统日志
					count_info_log = ""
					event_info_log = ""
					break_info_log = ""


					if self.target_detect.isChecked():				# 目标识别
						output, orign_img, img, pedestrians_num = target_detect(self.model, frame)
						if int(pedestrians_num) != 0:
							break_info_log = str(pedestrians_num) + "人闯红灯;\n"
							self.break_traffic_warning.setVisible(True)
							self.break_traffic_label.setVisible(True)
							self.break_traffic_label.setText(break_info_log)
						else:
							self.break_traffic_label.setVisible(False)
							self.break_traffic_warning.setVisible(False)
																	# 红绿灯检测
					if self.traffic_light_detect.isChecked():
						traffic_light_color = traffic_light_detect(output, orign_img)
						if traffic_light_color == "green":
							self.red_light.setVisible(False)
							self.green_light.setVisible(True)
						elif traffic_light_color == "red":
							self.green_light.setVisible(False)
							self.red_light.setVisible(True)
						else:
							self.green_light.setVisible(False)
							self.red_light.setVisible(False)
					else:
						self.green_light.setVisible(False)
						self.red_light.setVisible(False)

																	#车流，人流检测
					people_num = 0
					cars_num = 0
					motors_num = 0

					if self.cars_detect.isChecked():
						_, cars_num, motors_num = classNum_detect(output)
						self.tableWidget.setItem(0,1,QTableWidgetItem(str(cars_num)))
						self.tableWidget.setItem(0,2,QTableWidgetItem(str(motors_num)))
					else:
						self.tableWidget.setItem(0,1,QTableWidgetItem(str(0)))
						self.tableWidget.setItem(0,2,QTableWidgetItem(str(0)))
						#print(1111)
					if self.people_detect.isChecked():
						people_num,_, _ = classNum_detect(output)
						self.tableWidget.setItem(0,0,QTableWidgetItem(str(people_num)))
					else:
						self.tableWidget.setItem(0,0,QTableWidgetItem(str(0)))		

					count_info_log = "people:" + str(people_num) + ", cars:" + str(cars_num) + \
										", motors:" + str(motors_num) + ";\n"

																	# 车牌识别	
					if self.license_plate_detect.isChecked():		
						plate_info_list = recognize_plate(plate_frame)
						for plate_info in plate_info_list:
							plate = plate_info[0]		# 车牌
							conficdence = plate_info[1]	# 置信度
							#print("车牌:" + plate)
							#self.license_result.clear()
							self.license_result.setText(plate)
							rect = plate_info[2]		# 位置
							#print(rect[0], rect[2], rect[1], rect[3])
							plate_img = plate_frame[int(rect[1]) : int(rect[3] + rect[1]), \
								int(rect[0]) : int(rect[2]+rect[0])]

							plate_img = cv2.cvtColor(plate_img, cv2.COLOR_RGB2BGR)
							plate_img = cv2.resize(plate_img, (140, 30)) 
							plate_img = QImage(plate_img.data, plate_img.shape[1], \
											plate_img.shape[0], QImage.Format_RGB888)
							self.license_graph.setPixmap(QPixmap.fromImage(plate_img))	

							img = drawRectBox(img,rect,plate)

							plate_center = [int(rect[0] + rect[2]), int(rect[1] + rect[3])]	#车牌中心中心位置
							car_color = detect_car_color(output, plate_frame, plate_center)	#检测汽车颜色

							event_info_log = car_color + "汽车,车牌信息：" + plate + \
											"识别准确率:" + str(conficdence)[:5] + '\n'
							#print(event_info_log)		
					else:
						self.license_graph.clear()
						self.license_result.clear()	
					

					log_info = count_info_log + event_info_log + break_info_log
					self.logQueue.put(log_info)			
					
					#self.sys_log(count_info_log, event_info_log, break_info_log)
					#self.set_log_info(count_info_log, event_info_log, break_info_log)
									
					
				
					img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
					img = cv2.resize(img, (1080, 540)) 
					img = QImage(img.data, img.shape[1], img.shape[0], QImage.Format_RGB888)
					self.video_plate.setPixmap(QPixmap.fromImage(img))
				cv2.waitKey(1)
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