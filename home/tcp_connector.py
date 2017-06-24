import socket


def recv_line(socket):
    data = []
    while True:
        char = socket.recv(1)
        if char == b'\r':
            return b''.join(data).decode('UTF-8')
        else:
            data.append(char)


# ":@01A\r"


def send_tcp_request(message, address, port):
    # TCP_IP = 'porhaifarm.dyndns-web.com'
    print('MSG: ' + message)
    print('ADDR: ' + address)
    print('PORT: ' + str(port))

    MESSAGE = str.encode(message)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((address, port))
    s.send(MESSAGE)
    data = recv_line(s)
    s.close()
    print('RECEIVED: ' + data)
    return data
