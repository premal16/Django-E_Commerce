from django.contrib import admin
from .models import CustomUser,UserProfile,Category,Product,Order,OrderItem,CartItem
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)