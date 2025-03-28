from django import template

register = template.Library()

@register.filter
def get_range(value):
    """
    Returns a range of numbers from 0 to value-1
    Used for creating star ratings
    """
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    """
    Gets a value from a dictionary by key.
    Usage in template: {{ my_dict|get_item:key_variable }}
    """
    if dictionary is None:
        return None
        
    # Try with the key as is (likely integer ID)
    if key in dictionary:
        return dictionary.get(key)
    
    # Try with the key as string
    return dictionary.get(str(key), None) 