from django.core.management.base import BaseCommand, CommandError
from tlc.cargaGenericaBatch import * 
import os
import json
import threading

CONFIG_DIRECTORY_PATH = 'tlc/config_files/'
LOCAL_CODES_DIRECTORY_PATH = 'tlc/local_city_codes/'
LOG_DIRECTORY_PATH = 'log_files/'

class Command(BaseCommand):
	def handle(self, *args, **options):
		config_directory = CONFIG_DIRECTORY_PATH
		raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith('.json')]
		files = []
		for conf_file in raw_files:
			with open(config_directory + conf_file) as data_file:
			    files += [json.load(data_file)]

		timers = []
		for f in files:
			timers.append(threading.Thread(target = cron, args = [f]))
			timers[-1].start()

