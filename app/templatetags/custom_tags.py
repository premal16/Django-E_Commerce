from app.models import CartItem
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def cart_item_count(context):
    request = context['request']
    if request.user.is_authenticated:
        total = CartItem.objects.filter(user=request.user).count()
        return total
    return 0

@register.simple_tag(takes_context=True)
def cart_total(context):
    cart_subtotal = 0
    request = context['request']
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user=request.user)
        for cart_item in cart_items:
                cart_subtotal += cart_item.subtotal()
        cart_total = cart_subtotal        
        return cart_total
    


@register.filter
def starts_with(value, arg):
    return value.startswith(arg)