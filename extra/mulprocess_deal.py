"""
Pythom多进程处理rtmp视频流，并推流
"""

# -*- coding:utf-8 -*-
# ffmpeg -re -stream_loop -1 -i traffic.flv -c copy -f flv rtmp://101.132.236.124/live/livestream
# rtmp://101.132.236.124/live/stream
import selectors
import socket
import pickle
import json

import threading
import multiprocessing
import subprocess as sp
import time
import sys 
# 机器上的ros自带的Python环境会影响cv2的import，在你的机器上运行这一删除第20行代码
sys.path.remove('/opt/ros/kinetic/lib/python2.7/dist-packages')
import cv2


class ServerAchieve:
	def __init__(self):

		# selectors I/O复用
		self.mysel = selectors.DefaultSelector()

		# rtmp视频流
		self.cap = cv2.VideoCapture("rtmp://101.132.236.124/live/livestream")

		# socket通信线程
		self.server_tcp_thread = threading.Thread(target=self.connectClient, daemon=True)
		self.server_tcp_thread.start()

		# rtmp视频流读取队列
		self.video_queue = multiprocessing.Queue(maxsize=10)
		#　处理视频数据队列
		self.deal_data_queue = multiprocessing.Queue(maxsize=10)
		
		# 读取视频进程　处理视频进程
		video_process = [multiprocessing.Process(target=self.readVideo),
						 multiprocessing.Process(target=self.dealVideo,)]
						 			
		for process in video_process:
			process.daemon = True
			process.start()
		for process in video_process:
			process.join()


	def readVideo(self):
	    while True:
		    while(self.cap.isOpened()):
	    		ret, frame = self.cap.read()	
	    		if not ret:
	    		    print("Opening camera is failed")
	    		    break
	    		self.video_queue.put(frame)
	    		if self.video_queue.qsize() > 4:
	    			# 当队列中的视频帧超过4帧,将之前入队的帧出队列,保证队列的视频帧是和流媒体服务器实时刷新的
	    			self.video_queue.get()
	    		else:
	    			# 让另一个进程读取图片
	    			time.sleep(0.01)


	def dealVideo(self):		
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
		# stdin的参数是PIPE，则Popen.stdin是一个可写的对象
		p = sp.Popen(command, stdin=sp.PIPE)


		while True:		
			frame = self.video_queue.get()

			# 使用cv算法对视频进行处理
			# Your code ...

			data_dict = {'data_0':0}

			self.deal_data_queue.put(data_dict)
			if self.deal_data_queue.qsize() > 3:
				self.deal_data_queue.get()
			else:
				time.sleep(0.01)

			p.stdin.write(frame.tostring())


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
				if self.deal_data_queue.empty():
					result_json = json.dumps(result_dict)
					connection.sendall(result_json.encode())    # 回馈信息给客户端
				else:
					callback_json = json.dumps(self.deal_data_queue.get())
					print(callback_json)
					connection.sendall(callback_json.encode())    # 回馈信息给客户端
				print("read ......")
			else:
				# 如果收到客户端发来的exit，则关闭与客户端的连接
				print('closing.....')
				self.mysel.unregister(connection)
				connection.close()

		else:
		    # 如果没有数据，释放连接
		    print('closing.....')
		    self.mysel.unregister(connection)
		    connection.close()


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


if __name__ == '__main__':
	sa = ServerAchieve()
	while True:
		try:
			pass
		except AttributeError:
			pass
