from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .models import *
from .tasks import send_request_to_all_address
from itertools import tee, islice, chain
import datetime

def previous_and_next(some_iterable):
    prevs, items, nexts = tee(some_iterable, 3)
    prevs = chain([None], prevs)
    nexts = chain(islice(nexts, 1, None), [None])
    return zip(prevs, items, nexts)


def graph(request):
    user = request.GET.get('user', None)
    if user is None:
        return HttpResponseBadRequest('need "user" parameter')
    try:
        address = Address.objects.get(username=user)
    except Address.DoesNotExist:
        return HttpResponseBadRequest('user does not exist')

    floor = request.GET.get('floor', None)
    if floor is None:
        return HttpResponseBadRequest('need "floor" parameter')
    if not floor.isdigit():
        return HttpResponseBadRequest('floor must be integer')
    if int(floor) < 1 or int(floor) > address.floor_count:
        return HttpResponseBadRequest('invalid floor for user')

    data = Data.objects.filter(floor=floor, address=address).values('success', 'datetime', 'temp', 'humidity', 'relay')
    date_filter = request.GET.get('show', '')
    if date_filter.lower() == 'show-day':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(days=1))
    elif date_filter.lower() == 'show-week':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(weeks=1))
    elif date_filter.lower() == 'show-month':
        data = data.filter(datetime__gte=timezone.now() - timezone.timedelta(days=30))
    data = data.order_by('datetime')

    null_list = []
    for previous, d, nxt in previous_and_next(data):
        print(d['success'])
        if not d['success']:
            if nxt is not None and not nxt['success']:
                null_list.append([d['datetime'], nxt['datetime']])

    return render(request, 'home/graph.html', {
        'data': data,
        'null_list': null_list,
        'user': user.title(),
        'floor': floor,
    })


def test_send(request):
    send_request_to_all_address()
    return HttpResponse('OK')
