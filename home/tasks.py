from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import tcp_connector
from .models import *
import time
import socket, errno


def prepend_zero(num):
    if num < 10:
        return '0' + str(num)
    elif num < 100:
        return str(num)
    else:
        raise Exception('Floors can\'t exceed 99')


def create_failed_addr(err, address, floor):
    Data.objects.create(err=err, success=False, address=address, floor=floor)


@shared_task
def send_request_to_all_address():
    # TODO parallel for multiple addr
    address_list = Address.objects.all()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(4)
    for address in address_list:
        try:
            sock.connect((address.url, address.port))
        except Exception as exception:
            for floor in range(1, address.floor_count + 1):
                create_failed_addr(str(exception), address, floor)
            continue

        for floor in range(1, address.floor_count + 1):
            try:
                temphumi = tcp_connector.send_tcp_request(sock, ':@{}A\r'.format(prepend_zero(floor)))
                # EXPECTED RESPONSE: tttthhh_tttthhh
                # Temp is in format ttt.t, and humi in hh.h
                # First tttthhh is CALIBRATE, second is REAL, we only need CALIBRATE
                if (len(temphumi) != 15):
                    create_failed_addr("The length of temp/humid string is wrong", address, floor)
                    continue
                temp = temphumi[0:3] + '.' + temphumi[3:4]
                humidity = temphumi[4:6] + '.' + temphumi[6:7]

                relay = tcp_connector.send_tcp_request(sock, ':@{}4\r'.format(prepend_zero(floor)))
                # EXPECTED RESPONSE: xxxxxxxx
                # x is 0 or 1
                # Relay 1-6 corresponds to following index of response string:
                #  R1 R2    R3    R4 R5 R6
                #  |  |     |     |  |  |
                #  x  x  x  x  x  x  x  x
                if (len(relay) != 8):
                    create_failed_addr("The length of relay string is wrong", address, floor)
                    continue
                relay = relay[0] + relay[1] + relay[3] + relay[5] + relay[6] + relay[7]
                current_time = timezone.now().replace(second=0, microsecond=0)
            except socket.timeout:
                create_failed_addr('Request timed out', address, floor)
                continue
            except socket.error as e:
                if e.errno == errno.ECONNREFUSED:
                    create_failed_addr('Connection refused', address, floor)
                else:
                    create_failed_addr(str(e), address, floor)
                continue
            except Exception as exception:
                create_failed_addr(str(exception), address, floor)
                continue

            Data.objects.create(datetime=current_time, success=True, temp=temp, humidity=humidity, relay=relay, address=address, floor=floor)

        sock.close()


@shared_task
def erase_old_data():
    age_threshold = timezone.now() - timezone.timedelta(days=90)
    Data.objects.filter(datetime__lt=age_threshold).delete()