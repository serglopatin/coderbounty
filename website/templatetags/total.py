from django import template
from website.models import Payment
from django.db.models import Sum

register = template.Library()


@register.simple_tag
def bounty_total():
    _total = Payment.objects.aggregate(Sum('amount'))['amount__sum']
    if _total is None:
        return "0"
    return "{:,.0f}".format(_total)
