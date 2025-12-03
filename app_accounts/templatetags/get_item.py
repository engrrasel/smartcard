from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Template filter: return dictionary[key] if exists"""
    try:
        return dictionary.get(key, [])
    except:
        return []
