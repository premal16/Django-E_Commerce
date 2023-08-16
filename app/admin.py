from django.contrib import admin
from .models import CustomUser,UserProfile,Category,Product
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserProfile)
admin.site.register(Category)
admin.site.register(Product)