import time
import socket, errno
import traceback
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "birdhouse.settings")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
import django

django.setup()
from home.models import *

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
    return data


def prepend_zero(num):
    if num < 10:
        return '0' + str(num)
    elif num < 100:
        return str(num)
    else:
        raise Exception('Floors can\'t exceed 99')


def create_failed_addr(err, address, floor):
    current_time = timezone.now().replace(second=0, microsecond=0)
    Data.objects.create(datetime=current_time, err=err, success=False, address=address, floor=floor)

def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

if __name__ == '__main__':
    try:
        # TODO parallel for multiple addr
        address_list = Address.objects.all()
        for address in address_list:
            try:   
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(4)
                sock.connect((address.url, address.port))
            except Exception as exception:
                for floor in range(1, address.floor_count + 1):
                    create_failed_addr(str(exception), address, floor)
                continue

            for floor in range(1, address.floor_count + 1):
                try:
                    temphumi = send_tcp_request(sock, ':@{}A\r'.format(prepend_zero(floor)))
                    # EXPECTED RESPONSE: tttthhh_tttthhh
                    # Temp is in format ttt.t, and humi in hh.h
                    # First tttthhh is CALIBRATE, second is REAL, we only need CALIBRATE
                    if (len(temphumi) != 15):
                        create_failed_addr("The length of temp/humid string is wrong", address, floor)
                        continue
                    temp = temphumi[0:3] + '.' + temphumi[3:4]
                    humidity = temphumi[4:6] + '.' + temphumi[6:7]
                    if ( not is_float_try(temp) or not is_float_try(humidity) ):
                        raise TypeError('Temp or humi not a valid float')
                except Exception as exception:
                    create_failed_addr(str(exception), address, floor)
                    continue

                try:
                    relay = send_tcp_request(sock, ':@{}6\r'.format(prepend_zero(floor)))
                    # EXPECTED RESPONSE: xxxxxx
                    # x is 0 or 1
                    if (len(relay) != 6):
                        create_failed_addr("The length of relay string is wrong", address, floor)
                        continue
                    relay = relay[0] + relay[1] + relay[2] + relay[3] + relay[4] + relay[5]
                    current_time = timezone.now().replace(second=0, microsecond=0)
                    Data.objects.create(datetime=current_time, success=True, temp=temp, humidity=humidity, relay=relay, address=address, floor=floor)
                except Exception as exception:
                    Data.objects.create(datetime=current_time, success=True, temp=temp, humidity=humidity, relay='000000', address=address, floor=floor)

            sock.close()
    except Exception as exception:
        print('================ UNCAUGHT EXCEPTION ================')
        print(str(exception))
        traceback.print_exc()
    print('Done')