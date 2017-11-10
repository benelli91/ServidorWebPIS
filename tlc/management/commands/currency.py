from tlc.exchange import loadExchange
from django.core.management.base import BaseCommand, CommandError
import time
from datetime import datetime,timedelta,tzinfo
class Command(BaseCommand):

    def handle(self, *args, **options):
        reload_time = timedelta(hours = 24)
        while True:
            start_time = datetime.now()
            loadExchange()
            end_time = datetime.now()
            total_time = end_time - start_time
            if(total_time < timedelta(hours = 4)):
                interval = reload_time - total_time
                time.sleep(interval.seconds)
