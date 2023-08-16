from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.homePage, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register_and_login, name='register'),
    path('profile/', views.profilePage, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('contact/', views.contactPage, name='contact'),
    path('change-password/', views.change_password, name='change_password'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product-delete'),
    path('add_product/', views.add_product, name='add_product'),

    
]
