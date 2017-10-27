from django import template
from datetime import datetime, timedelta
import re

register = template.Library()

def key(d, key_name):
    return d[key_name]
register.filter('key', key)

def replace ( string, args ):
    search  = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub( search, replace, string )
register.filter('replace', replace)

def add_duration(date, duration):
    minutes  = duration % 60
    hours = (duration - minutes) / 60
    #print(date)
    #print(duration)
    return date + timedelta(hours=hours, minutes = minutes, seconds = 0)
register.filter('add_duration', add_duration)

def add_timezone_offset(date, offset):
    return date + timedelta(minutes=offset)
register.filter('add_timezone_offset', add_timezone_offset)
