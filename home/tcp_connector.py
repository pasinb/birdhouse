import socket


def recv_line(socket):
    data = []
    while True:
        char = socket.recv(1)
        if char == b'\r':
            return b''.join(data).decode('UTF-8')
        else:
            data.append(char)


def send_tcp_request(socket, message):

    MESSAGE = str.encode(message)
    socket.send(MESSAGE)
    data = recv_line(socket)
    print('RECEIVED: ' + data)
    return data
