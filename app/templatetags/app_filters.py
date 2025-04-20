# Core Django imports
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
        return float(value) * float(arg)
    except ValueError:
        return 0

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

@register.filter
def filter_attended(attendance_records):
    """Filter attendance records to get only attended ones"""
    return attendance_records.filter(student_attend=True)

@register.filter
def div(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def filter_by_subject(routines, subject):
    """
    Filter routines to get the one for a specific subject.
    Usage in template: {{ routines|filter_by_subject:subject }}
    """
    if not routines:
        return None
    
    for routine in routines:
        if routine.subject_id == subject.id:
            return routine
    return None 