from django.contrib import admin
from .models import *


# Register your models here.
class DataAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'datetime']


class AddressAdmin(admin.ModelAdmin):
    # ...
    def get_form(self, request, obj=None, **kwargs):
        """Override the get_form and extend the 'exclude' keyword arg"""
        if not obj:
            kwargs.update({
                'exclude': getattr(kwargs, 'exclude', tuple()) + ('port',),
            })
        return super(AddressAdmin, self).get_form(request, obj, **kwargs)


admin.site.register(Data, DataAdmin)
admin.site.register(Address, AddressAdmin)
