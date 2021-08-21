from django import template

register = template.Library()


@register.simple_tag
def append_param(request, key, value):
    query_dict = request.GET.copy()
    query_dict[key] = value
    return '?' + query_dict.urlencode()
