# custom_tags.py
from django import template
register = template.Library()

import datetime

@register.simple_tag
def current_time(format_string):
    return datetime.datetime.now().strftime(format_string)