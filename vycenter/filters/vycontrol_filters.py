from django.template.defaultfilters import register


@register.filter
def routepack(value): 
    """Pack a route into a string"""
    return str(value).replace("/","!")

@register.filter
def routeunpack(value): 
    """UnpPack a route into a string"""
    return str(value).replace("!","/")