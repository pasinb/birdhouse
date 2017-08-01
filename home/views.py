from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .models import *
from .tasks import send_request_to_all_address, erase_old_data
from itertools import tee, islice, chain
import datetime
from django.views.decorators.cache import never_cache


def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


@never_cache
def graph(request):
    user = request.GET.get('user', None)
    if user is None:
        return HttpResponseBadRequest("The 'user' parameter is required.")
    try:
        address = Address.objects.get(username=user)
    except Address.DoesNotExist:
        return HttpResponseBadRequest('User does not exist.')

    floor = request.GET.get('floor', None)
    if floor is None:
        floor = request.COOKIES.get('floor', None)
        if (floor is None):
            floor = 1
    if type(floor) is not int and not floor.isdigit():
        floor = 1
    if int(floor) < 1 or int(floor) > address.floor_count:
        floor = 1

    data = Data.objects.filter(floor=floor, address=address).values('success', 'datetime', 'temp', 'humidity', 'relay')
    date_filter = request.GET.get('show', '').lower()

    if date_filter is '':
        date_filter = request.COOKIES.get('show', None)
    if date_filter == 'show-day':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(days=1))
    elif date_filter == 'show-week':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(weeks=1))
    elif date_filter == 'show-month':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(days=30))

    data = data.order_by('datetime')

    null_list = []

    for i in range(0, len(data)):
        if not data[i]['success']:
            if i + 1 < len(data) and not data[i + 1]['success']:
                null_list.append([data[i]['datetime'], data[i + 1]['datetime']])

    # enforce_zoom_limit = True
    # if (len(data) < 13):
    #     enforce_zoom_limit = False

    return render(request, 'home/graph.html', {
        'data': data,
        'null_list': null_list,
        'user': address.username.title(),
        'floor': int(floor),
        'floor_count': range(1, address.floor_count + 1),
        'date_filter': date_filter,
        #'enforce_zoom_limit': enforce_zoom_limit,
    })


def test_send(request):
    send_request_to_all_address()
    return HttpResponse('OK')


def test_delete(request):
    erase_old_data()
    return HttpResponse('OK')
