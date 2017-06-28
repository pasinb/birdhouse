from django.contrib import admin
from .models import *

# Register your models here.
class DataAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'datetime']

admin.site.register(Data, DataAdmin)
admin.site.register([Address,])
