from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
# Create your models here.
# class User(AbstractUser):
#     # name = models.CharField(max_length=50)
#     email = models.CharField(max_length=50, unique=True)
#     username = models.CharField(max_length=50, unique=True)
#     mobile_number = models.CharField(max_length=15, unique=True, blank=True, null=True)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username']

#     def __str__(self):
#         return self.email
    
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/', default = 'profile_pic/userprofile.jpg')
    about = models.TextField(blank=True)
    job_title = models.CharField(max_length=200, blank=True)
    country = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    mobile_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.user.username
    
    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile.objects.create(user=instance)

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def save_user_profile(sender, instance, **kwargs):
        instance.userprofile.save()


class CustomUser(AbstractUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    


# product Category
class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# product model
class Product(models.Model):
    label = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)  
    product_image = models.ImageField(upload_to='product_images/', default='product_images/product.png')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2) 

    def __str__(self):
        return self.label
    




class Order(models.Model):
    STATUS_CHOICES = (
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50,default=False)
    email = models.EmailField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    # added two fields
    address = models.CharField(max_length=200, default='', blank=True)
    mobile_number = models.CharField(max_length=12, default='', blank=True)


    def __str__(self):
        return f"Order {self.id} - {self.user}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Item for Order {self.order_id} - {self.product.label}"
    
    def total_price(self):
        return self.quantity * self.price
    

class CartItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)  # Assuming you have a Product model
    quantity = models.PositiveIntegerField(default=1)
    # Add more fields as needed, e.g., price, date_added, etc.
    def subtotal(self):
        return self.product.price * self.quantity
    
    def remove(self):
        # Method to remove the cart item
        self.delete()