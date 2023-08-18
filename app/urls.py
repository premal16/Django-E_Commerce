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
    # path('edit-profile/', views.edit_profile, name='edit_profile'),
    # path('edit-profile/<int:user_id>/', views.edit_profile, name='admin_edit_profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-profile/<int:user_id>/', views.edit_profile, name='edit_profile_with_id'),
    path('contact/', views.contactPage, name='contact'),
    path('change-password/', views.change_password, name='change_password'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product-delete'),
    path('add_product/', views.add_product, name='add_product'),
    path('orders/', views.OrderListView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='admin-order-detail'),
    path('order/<int:order_id>/change-status/', views.change_order_status, name='admin-order-change-status'),
    path('users/',views.user, name='user'),
    path('users/<int:pk>/',views.UserDetailview.as_view(), name='user-profile'),
    path('users/delete/<int:user_id>/', views.custom_user_delete, name='custom-user-delete'),
]
