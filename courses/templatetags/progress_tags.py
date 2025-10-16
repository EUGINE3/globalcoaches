from django import template
from courses.progress_utils import ProgressDisplayHelper

register = template.Library()


@register.filter
def progress_display_class(percentage):
    """Get CSS class for progress display"""
    return ProgressDisplayHelper.get_progress_display_class(percentage)


@register.filter
def progress_color(percentage):
    """Get color for progress display"""
    return ProgressDisplayHelper.get_progress_color(percentage)


@register.filter
def format_progress(percentage, decimal_places=0):
    """Format progress percentage for display"""
    return ProgressDisplayHelper.format_progress_percentage(percentage, decimal_places)


@register.inclusion_tag('courses/progress_bar.html')
def progress_bar(percentage, show_text=True, size='medium'):
    """
    Render a progress bar with the given percentage
    
    Usage: {% progress_bar item.completion_percentage %}
    """
    return {
        'percentage': percentage or 0,
        'show_text': show_text,
        'size': size,
        'color': ProgressDisplayHelper.get_progress_color(percentage or 0),
        'display_class': ProgressDisplayHelper.get_progress_display_class(percentage or 0)
    }


@register.inclusion_tag('courses/progress_circle.html')
def progress_circle(percentage, size='medium', show_text=True):
    """
    Render a circular progress indicator
    
    Usage: {% progress_circle item.completion_percentage %}
    """
    return {
        'percentage': percentage or 0,
        'size': size,
        'show_text': show_text,
        'color': ProgressDisplayHelper.get_progress_color(percentage or 0)
    }
