from __future__ import absolute_import, unicode_literals
from celery import shared_task
from . import tcp_connector
from .models import *
import time


def prepend_zero(num):
    if num < 10:
        return '0' + str(num)
    elif num < 100:
        return str(num)
    else:
        raise Exception('Floors can\'t exceed 99')


def create_failed_addr(err, address, floor):
    Data.objects.create(err=err, success=False, address=address, floor=floor)

#TODO erase old data task

@shared_task
def send_request_to_all_address():
    #TODO parallel for multiple addr
    address_list = Address.objects.all()
    for address in address_list:
        for floor in range(1, address.floor_count + 1):

            try:
                received = tcp_connector.send_tcp_request(':@{}A\r'.format(prepend_zero(floor)), address.url, address.port)
            except Exception as exception:
                create_failed_addr(str(exception), address, floor)
                continue
            if (len(received) != 15):
                create_failed_addr('temp/humid wrong size', address, floor)
                continue
            temp = received[0:3] + '.' + received[3:4]
            humidity = received[4:6] + '.' + received[6:7]

            time.sleep(1)

            try:
                received = tcp_connector.send_tcp_request(':@{}4\r'.format(prepend_zero(floor)), address.url, address.port)
            except Exception as exception:
                create_failed_addr(str(exception), address, floor)
                continue
            if (len(received) != 8):
                create_failed_addr('relay wrong size', address, floor)
                continue
            relay = received[0] + received[1] + received[3] + received[5] + received[6] + received[7]
            Data.objects.create(success=True, temp=temp, humidity=humidity, relay=relay, address=address, floor=floor)

            if (floor != address.floor):
                time.sleep(1)


@shared_task
def cleanup():
    pass  # TODO
