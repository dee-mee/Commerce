from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def filter_by_status(orders, status):
    """Filter orders by status"""
    return orders.filter(status=status)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return value
