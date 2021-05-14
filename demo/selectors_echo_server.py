import selectors
import socket
import time

mysel = selectors.DefaultSelector()
keep_running = True

def read(connection, mask):
    "读取事件的回调"
    global keep_running

    client_address = connection.getpeername()
    print('read({})'.format(client_address))
    data = connection.recv(1024)
    if data:
        # 可读的客户端 socket 有数据
        print('  received {!r}'.format(data))

        if data.decode() != "exit":
            connection.sendall("i am server".encode())
            print("send")
        else:
            # 将空结果解释为关闭连接
            print('  closing')
            mysel.unregister(connection)
            connection.close()
            # 告诉主进程停止
            keep_running = False


def accept(sock, mask):
    "有新连接的回调"
    new_connection, addr = sock.accept()
    print('accept({})'.format(addr))
    new_connection.setblocking(False)
    mysel.register(new_connection, selectors.EVENT_READ, read)

server_address = ('localhost', 10001)
print('starting up on {} port {}'.format(*server_address))
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
server.setblocking(False)
server.bind(server_address)
server.listen(5)

mysel.register(server, selectors.EVENT_READ, accept)

while keep_running:
    print('waiting for I/O')
    for key, mask in mysel.select():
        callback = key.data
        callback(key.fileobj, mask)

print('shutting down')
mysel.close()