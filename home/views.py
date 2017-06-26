from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from .models import *


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

    data = Data.objects.filter(floor=floor, address=address).values('datetime', 'temp', 'humidity', 'relay').order_by('datetime')
    return render(request, 'home/graph.html', {
        'data': data
    })
