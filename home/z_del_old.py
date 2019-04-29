import time
import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "birdhouse.settings")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(BASE_DIR)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
import django

django.setup()
from home.models import *
if __name__ == '__main__':
    try:
        age_threshold = timezone.now() - timezone.timedelta(days=90)
        Data.objects.filter(datetime__lt=age_threshold).delete()
    except Exception as exception:
        print('================ UNCAUGHT EXCEPTION ================')
        print(str(exception))
    print('Done')