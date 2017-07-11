from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import tcp_connector
from .models import *
import time
import socket


def prepend_zero(num):
    if num < 10:
        return '0' + str(num)
    elif num < 100:
        return str(num)
    else:
        raise Exception('Floors can\'t exceed 99')


def create_failed_addr(err, address, floor):
    Data.objects.create(err=err, success=False, address=address, floor=floor)


# TODO erase old data task

@shared_task
def send_request_to_all_address():
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
                temphumi = tcp_connector.send_tcp_request(sock, ':@{}A\r'.format(prepend_zero(floor)))
                # create_failed_addr(str(exception), address, floor)
                if (len(temphumi) != 15):
                    create_failed_addr('temp/humid wrong size', address, floor)
                    continue
                temp = temphumi[0:3] + '.' + temphumi[3:4]
                humidity = temphumi[4:6] + '.' + temphumi[6:7]

                relay = tcp_connector.send_tcp_request(sock, ':@{}4\r'.format(prepend_zero(floor)))
                if (len(relay) != 8):
                    create_failed_addr('relay wrong size', address, floor)
                    continue
                relay = relay[0] + relay[1] + relay[3] + relay[5] + relay[6] + relay[7]
                current_time = timezone.now()
                current_time = current_time.replace(second=0, microsecond=0)
            except Exception as exception:
                create_failed_addr(str(exception), address, floor)
                continue

            Data.objects.create(datetime=current_time, success=True, temp=temp, humidity=humidity, relay=relay, address=address, floor=floor)

        sock.close()


@shared_task
def cleanup():
    pass  # TODO
