from django import template

register = template.Library()


@register.simple_tag
def add_tag_param(request, tag):
    query_dict = request.GET.copy()
    query_dict.appendlist('tag', tag)
    return "?" + query_dict.urlencode()


@register.simple_tag
def remove_tag_param(request, tag):
    query_dict = request.GET.copy()
    tags = query_dict.getlist('tag')
    tags.remove(tag)
    query_dict.setlist('tag', tags)
    if 'page' in query_dict:
        query_dict['page'] = 1
    return "?" + query_dict.urlencode()


@register.simple_tag
def get_tag_params(request):
    return request.GET.getlist('tag')
