from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .models import *
from itertools import tee, islice, chain


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

    data = Data.objects.filter(floor=floor, address=address).values('success', 'datetime', 'temp', 'humidity', 'relay').order_by('datetime')
    null_list = []

    for previous, d, nxt in previous_and_next(data):
        if not d['success']:
            if nxt is not None and not nxt['success']:
                null_list.append([d['datetime'], nxt['datetime']])

    return render(request, 'home/graph.html', {
        'data': data,
        'null_list': null_list
    })

