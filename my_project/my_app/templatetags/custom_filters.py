from django import template

register = template.Library()

@register.filter
def dict_key(dictionary, key):
    if dictionary is not None:
        return dictionary.get(key, None)
    return None

@register.filter
def dict_key_nested(dictionary, key_tuple):
    if dictionary is not None and isinstance(key_tuple, tuple) and len(key_tuple) == 2:
        outer_key, inner_key = key_tuple
        outer_dict = dictionary.get(outer_key, {})
        if outer_dict is not None:
            return outer_dict.get(inner_key, None)
    return None


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)