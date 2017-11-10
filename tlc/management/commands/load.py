from django.core.management.base import BaseCommand, CommandError
from tlc.cargaGenericaBatch import *
import os
import json
import threading

CONFIG_DIRECTORY_PATH = 'tlc/config_files/'
LOCAL_CODES_DIRECTORY_PATH = 'tlc/local_city_codes/'
LOG_DIRECTORY_PATH = 'log_files/'

class Command(BaseCommand):
	def add_arguments(self, parser):
        	parser.add_argument('file_name', nargs='+')

	def handle(self, *args, **options):
		for file_name in options['file_name']:			
			config_directory = CONFIG_DIRECTORY_PATH
			try:
				raw_files = [pos_json for pos_json in os.listdir(config_directory) if pos_json.endswith(file_name + '.json')]
				files = []
				with open(config_directory + raw_files[0]) as data_file:
					config_file = json.load(data_file)
			except:
				raise CommandError('Config file for "%s" does not exist' % file_name)
			loadWebpage(config_file)
