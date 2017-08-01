from django.db import models
import uuid
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=127)
    url = models.CharField(max_length=255, verbose_name="URL")
    port = models.IntegerField(default=1470, blank=True)
    floor_count = models.IntegerField(default=1, blank=True, validators=[MaxValueValidator(100),MinValueValidator(1)])

    class Meta:
        verbose_name_plural = 'List Addresses'

    def __str__(self):
        return '{} [{}]'.format(self.username,self.url)


class Data(models.Model):
    address = models.ForeignKey(Address)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    success = models.BooleanField(default=True)
    err = models.CharField(max_length=255, null=True, blank=True, default=None)
    datetime = models.DateTimeField(default=timezone.now)
    floor = models.IntegerField(null=True)
    temp = models.FloatField(null=True, blank=True, default=None)
    humidity = models.FloatField(null=True, blank=True, default=None)
    relay = models.CharField(max_length=6, null=True, blank=True, default=None)

    class Meta:
        verbose_name_plural = 'Data'

    def __str__(self):
        if not self.success:
            return '{} | FAIL: {}'.format(self.address, self.err)
        else:
            return '{} | FLOOR: {} | TEMP: {} | HUMI: {} | RELAY: {}'.format(self.address, self.floor, self.temp, self.humidity, self.relay)
