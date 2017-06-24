from django.db import models
import uuid
from django.utils import timezone


# Create your models here.

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=127)
    url = models.CharField(max_length=255)
    port = models.IntegerField(default=1470, blank=True)
    floor = models.IntegerField(default=1, blank=True)

    class Meta:
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return self.username + ' | ' + self.url


class Data(models.Model):
    address = models.ForeignKey(Address)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    success = models.BooleanField(default=True)
    err = models.CharField(max_length=255, null=True, default=None)
    datetime = models.DateTimeField(default=timezone.now)
    floor = models.IntegerField()
    temp = models.FloatField(null=True, default=None)
    humidity = models.FloatField(null=True, default=None)
    relay = models.CharField(max_length=6, null=True, default=None)

    class Meta:
        verbose_name_plural = 'Data'

    def __str__(self):
        if not self.success:
            return 'FAIL: {}'.format(self.err)
        else:
            return '{} | FLOOR: {} | TEMP: {} | HUMI: {} | RELAY: {}'.format(self.address, self.floor, self.temp, self.humidity, self.relay)
