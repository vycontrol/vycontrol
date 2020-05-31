from django.template.defaultfilters import register
import random


@register.filter
def routepack(value): 
    """Pack a route into a string"""
    return str(value).replace("/","!")

@register.filter
def routeunpack(value): 
    """UnpPack a route into a string"""
    return str(value).replace("!","/")

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_port(dictionary, key):
    d = dictionary.get(key)    
    # n = port
    # p = protocol
    # d = description
    return d['n']


@register.filter
def get_item_network(dictionary, key):
    d = dictionary.get(key)    
    return d['network']

@register.simple_tag
def random_int(a, b=None):
    if b is None:
        a, b = 0, a
    return random.randint(a, b)
