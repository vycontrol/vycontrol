from django.template.defaultfilters import register


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

