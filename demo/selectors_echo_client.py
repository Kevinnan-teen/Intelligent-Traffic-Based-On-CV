import selectors
import socket

mysel = selectors.DefaultSelector()
keep_running = True


out = ""

# 连接是一个阻塞操作， 因此在返回之后调用 setblocking() 方法
server_address = ('localhost', 10001)
print('connecting to {} port {}'.format(*server_address))
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(server_address)
# 设置非阻塞
sock.setblocking(False)

# 设置选择器去监听 socket 是否可写的和是否可读
mysel.register(
    sock,
    selectors.EVENT_READ | selectors.EVENT_WRITE,
)

while keep_running:
    # print('waiting for I/O')
    for key, mask in mysel.select(timeout=1):
        connection = key.fileobj
        client_address = connection.getpeername()
        # print('client({})'.format(client_address))

        if mask & selectors.EVENT_READ:
            # print('  ready to read')
            data = connection.recv(1024)
            print("if duse...")
            if data:
                # A readable client socket has data
                print('receive:  ', data)
                # bytes_received += len(data)

        if mask & selectors.EVENT_WRITE:
            # print('  ready to write')
            out = input('ready to write: ')
            # print(out)
            # print('  sending {!r}'.format(next_msg))
            sock.sendall(out.encode())
            # bytes_sent += len(next_msg)

            if out == "exit":
                print("closing...")
                keep_running = False

            

print('shutting down')
mysel.unregister(connection)
connection.close()
mysel.close()