# -*- coding:utf-8 -*-
# ffmpeg -re -stream_loop -1 -i traffic.flv -c copy -f flv rtmp://101.132.236.124/live/livestream
# rtmp://101.132.236.124/live/stream
import selectors
import socket
import pickle
import json

import sys   	
import threading
import multiprocessing
import subprocess as sp
import time

import torch
from video_demo import target_detect, target_detect_2, traffic_light_detect, classNum_detect
from darknet import Darknet
from plateRecognition import recognize_plate, drawRectBox
from detect import detect_car_color

import cv2


class ServerAchieve:
	def __init__(self):

		self.mysel = selectors.DefaultSelector()
		self.keep_running = True

		self.result_queue = multiprocessing.Queue(maxsize=10)

		self.server_tcp_thread = threading.Thread(target=self.connectClient, daemon=True)
		self.server_tcp_thread.start()

		self.cap = cv2.VideoCapture("rtmp://101.132.236.124/live/livestream")
		print("cap init is completed")


		# self.recognize_thread = threading.Thread(target=self.tt1, daemon=True)
		# self.recognize_thread.start()

		# multiprocessing.set_start_method(method='spawn')  # init
		# 视频读取多进程队列
		self.video_queue = multiprocessing.Queue(maxsize=10)
		#self.function_queue = multiprocessing.Queue(maxsize=2)
		self.deal_data_queue = multiprocessing.Queue(maxsize=10)
		

		video_process = [multiprocessing.Process(target=self.readVideo),
						 multiprocessing.Process(target=self.dealVideo,),
						 multiprocessing.Process(target=self.dealData,)]
						 #multiprocessing.Process(target=self.plateDeal)]

		
		
		for process in video_process:
			process.daemon = True
			process.start()
		for process in video_process:
			process.join()



	def plateDeal(self):
		while True:		
			# print("plate_recognize\n")
			frame = self.video_queue.get()
			# 车牌识别
			# data_dict['plate_info_list'] = recognize_plate(data_dict['frame'])
			r_p = recognize_plate(frame)
			if (len(r_p)):
				print("have plate")
				print(r_p[0])


	def readVideo(self):
	    while True:
		    while(self.cap.isOpened()):
		    	if True:#self.function_queue.get()['target_detect_is_open']:
		    		ret, frame = self.cap.read()	
		    		if not ret:
		    		    print("Opening camera is failed")
		    		    break
		    		self.video_queue.put(frame)
		    		if self.video_queue.qsize() > 4:
		    			self.video_queue.get()
		    		else:
		    			# 让另一个进程读取图片
		    			time.sleep(0.01)
	

	def dealData(self):
		# 闯红灯行人数, 
		# 红绿灯
		# 行人数 车辆数 摩托数
		# 
		result_dict = {'pedestrians_num':'', 'traffic_light_color':'', 
					   'people_num':0, 'cars_num':0, 'motors_num':0, 
					   'plate_info_list':[], 'data_h':True}

		i = 0

		while True:
			data_dict = self.deal_data_queue.get()
			# print("get deal data")

			traffic_light_color = traffic_light_detect(data_dict['output'], data_dict['frame'])

			result_dict['plate_info_list'] = data_dict['plate_info_list']



			# result_dict['plate_info_list'] = recognize_plate(data_dict['frame'])


			people_num, cars_num, motors_num = classNum_detect(data_dict['output'])


			result_dict['pedestrians_num'] = data_dict['pedestrians_num']
			result_dict['traffic_light_color'] = traffic_light_color
			result_dict['people_num'] = people_num
			result_dict['cars_num'] = cars_num
			result_dict['motors_num'] = motors_num
			

			self.result_queue.put(result_dict)
			if self.result_queue.qsize() > 3:
				self.result_queue.get()
			else:
				time.sleep(0.01)

			
			pass


	def dealVideo(self):
		# 只有客户端选择check box时，才可以进行推流．（在进入这个函数之前）
		rtmpUrl = "rtmp://101.132.236.124/live/stream"

		# Get video information
		fps = int(self.cap.get(cv2.CAP_PROP_FPS))
		width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
		height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

		# ffmpeg command
		command = ['ffmpeg',
		        '-y',
 		        '-f', 'rawvideo',
		        '-vcodec','rawvideo',
		        '-pix_fmt', 'bgr24',
		        '-r', '7',
		        '-s', "{}x{}".format(width, height),
#		        '-r', str(fps),
		        '-i', '-',        
		        '-pix_fmt', 'yuv420p',
		        '-f', 'flv', 
		        rtmpUrl]
		print("deal Video process!")

		# 管道配置
		p = sp.Popen(command, stdin=sp.PIPE)

		
		# while not self.function_queue.get()['target_detect_is_open']:
		# 	time.sleep(1)
		
		# 加载模型
		CUDA = torch.cuda.is_available()
		print("Loading network.....")
		model = Darknet("../yolov3/cfg/yolov3.cfg")
		#self.model = Darknet("../yolov3/cfg/yolov2-tiny.cfg")
		model.load_weights("../yolov3/weights/yolov3.weights")
		#self.model.load_weights("../yolov3/weights/yolov2-tiny.weights")

		print("Network successfully loaded")
		model.net_info["height"] = 416
		inp_dim = int(model.net_info["height"])
		assert inp_dim % 32 == 0
		assert inp_dim > 32

		if CUDA:
		    model.cuda()                        # 将模型迁移到GPU
		model.eval()


		data_dict = {'frame':None, 'output':None, 'pedestrians_num':None, 'plate_info_list':[]}

		i = 0

		while True:		
			frame = self.video_queue.get()
			data_dict['frame'] = frame.copy()
			data_dict['plate_info_list'] = []
			# 车牌识别
			# if(i == 30):
			# 	# data_dict['plate_info_list'] = recognize_plate(data_dict['frame'])
			# 	if (len(recognize_plate(data_dict['frame']))):
			# 		print("have plate")
			# 		print(recognize_plate[0])
			# 	i = 0
			# i += 1
			

			output, orign_img, frame, pedestrians_num = target_detect(model, frame)
			
			data_dict['output'] = output
			data_dict['pedestrians_num'] = pedestrians_num

			self.deal_data_queue.put(data_dict)



			p.stdin.write(frame.tostring())


			# traffic_light_color = traffic_light_detect(output, orign_img)

			# people_num, cars_num, motors_num = classNum_detect(output)

			# plate_info_list = recognize_plate(orign_img)

			# result_dict['pedestrians_num'] = pedestrians_num
			# result_dict['traffic_light_color'] = traffic_light_color
			# result_dict['people_num'] = people_num
			# result_dict['cars_num'] = cars_num
			# result_dict['motors_num'] = motors_num
			# # result_dict['plate_info_list'] = plate_info_list

			#self.result_queue.put(result_dict, block=False)
			#self.result_queue.get()


	def socketRead(self, connection, mask):
		empty_dict = {'empty':'empty'}

		result_dict = {'pedestrians_num':'', 'traffic_light_color':'', 
						'people_num':0, 'cars_num':0, 'motors_num':0, 
						'plate_info_list':'', 'data_h':False}
		client_address = connection.getpeername()
		
		client_data = connection.recv(1024)
		if client_data:
			# 可读的客户端 socket 有数据
			if client_data.decode() != "exit":
				if self.result_queue.empty():
					# print("waiting send...111")
					result_json = json.dumps(result_dict)
					connection.sendall(result_json.encode())    # 回馈信息给客户端
				else:
					# print("waiting send...222")
					callback_json = json.dumps(self.result_queue.get())
					connection.sendall(callback_json.encode())    # 回馈信息给客户端
				print("read ......")
			else:
				print('closing.....')
				self.mysel.unregister(connection)
				connection.close()
			# print('read({})'.format(client_address))

		else:
		    # 如果没有数据，释放连接
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    print('closing.....')
		    self.mysel.unregister(connection)
		    connection.close()
		    # 告诉主进程停止
		    # self.keep_running = False


	def socketAccept(self, sock, mask):
	    # "有新连接的回调"
	    new_connection, addr = sock.accept()
	    print('accept({})'.format(addr))
	    new_connection.setblocking(False)
	    self.mysel.register(new_connection, selectors.EVENT_READ, self.socketRead)
			

	def connectClient(self):
		server_address = ('127.0.0.1', 10001)
		print('starting up on {} port {}'.format(*server_address))
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
		server.setblocking(False)
		server.bind(server_address)
		server.listen(5)

		self.mysel.register(server, selectors.EVENT_READ, self.socketAccept)

		while True:
		    print('waiting for I/O')
		    
		    for key, mask in self.mysel.select(timeout=1):
		        callback = key.data
		        callback(key.fileobj, mask)		        


	def show_frame(self):
		pass
		# cv2.imshow('frame', self.frame)
		# cv2.waitKey(self.FPS_MS)


if __name__ == '__main__':
	sa = ServerAchieve()
	while True:
		try:
			# sa.show_frame()
			pass
		except AttributeError:
			pass
