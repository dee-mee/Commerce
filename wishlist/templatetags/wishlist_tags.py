from django import template
from django.db.models import Count

register = template.Library()

@register.filter
def filter_by_rating(reviews, rating):
    """
    Filter reviews by rating
    """
    return reviews.filter(rating=rating)

@register.filter
def percentage(value, total):
    """
    Calculate percentage
    """
    if total == 0:
        return 0
    return int((value / total) * 100)
