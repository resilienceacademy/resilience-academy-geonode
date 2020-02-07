from django import template
from resilienceacademy.views import _fetch_wp_json
register = template.Library()

@register.simple_tag
def load_wp_posts():
    return _fetch_wp_json()