from django.urls import path
from . import views
from django.contrib import admin


urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('',views.homePage, name='home'),
    path('login/', views.login, name='login'),
    path('register/', views.register_and_login, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profilePage, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('edit-profile/<int:user_id>/', views.edit_profile, name='edit_profile_with_id'),
    path('contact/', views.contactPage, name='contact'),
    path('change-password/', views.change_password, name='change_password'),
    path('products/<int:product_id>/', views.product_detail, name='product-detail'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product-delete'),
    path('add_product/', views.add_product, name='add_product'),
    path('orders/', views.SuperuserOrderListView.as_view(), name='admin-order-list'),
    path('orders/<int:pk>/', views.OrderDetailView.as_view(), name='admin-order-detail'),
    path('order/<int:order_id>/change-status/', views.change_order_status, name='admin-order-change-status'),
    path('users/',views.user, name='user'),
    path('users/<int:pk>/',views.UserDetailview.as_view(), name='user-profile'),
    path('users/delete/<int:user_id>/', views.custom_user_delete, name='custom-user-delete'),
    path('products/', views.product_list, name='product-list'),
    path('product/update/<int:product_id>/', views.product_update, name='product-update'),
    path('session-try/', views.session_try, name='session-try'),



    path('user-home/', views.user_home, name='user-home'),
    path('user-product/', views.user_product, name='user-product'),
    path('quick-view/<int:product_id>/', views.quick_view, name='quick-view'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('remove/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('update_cart_item/<int:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-session/', views.create_checkout_session, name='checkout_session'),
    path('success/',views.success, name='success'),
    path('cancel/',views.cancel, name='cancel'),

]

