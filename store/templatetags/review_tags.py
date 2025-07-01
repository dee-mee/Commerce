from django import template

register = template.Library()

@register.filter
def filter_by_rating(reviews, rating):
    """
    Filter reviews by rating
    """
    return [review for review in reviews if review.rating == int(rating)]

@register.filter
def percentage(value, total):
    """
    Calculate percentage
    """
    if total == 0:
        return 0
    return int((value / total) * 100)

@register.filter
def widthratio(value, arg):
    """
    Calculate width ratio for progress bars
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
