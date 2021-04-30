# -*- coding:utf-8 -*-

import socket
import pickle
import json

import sys   


ip_port = ('127.0.0.1', 9999)

sk = socket.socket()            # 创建套接字
sk.bind(ip_port)                # 绑定服务地址
sk.listen(5)                    # 监听连接请求
print('启动socket服务，等待客户端连接...')
conn, address = sk.accept()     # 等待连接，此处自动阻塞

i = 0

while True:     # 一个死循环，直到客户端发送‘exit’的信号，才关闭连接
    client_data_json = conn.recv(1024).decode()      # 接收信息
    client_data_dict = json.loads(client_data_json)
    #client_data = pickle.load(cli)


    if i == 20:
    	conn.sendall('exit'.encode())
    	break

    i += 1

    print("来自%s的客户端向你发来信息：%s" % (address, client_data_dict))
    conn.sendall('服务器已经收到你的信息'.encode())    # 回馈信息给客户端
    

conn.close()    # 关闭连接