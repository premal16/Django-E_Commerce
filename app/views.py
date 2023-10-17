from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import get_user_model
from .models import CustomUser,UserProfile,Product,Order,Category,CartItem,OrderItem
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required,user_passes_test
from django.shortcuts import render, get_object_or_404
from .forms import ProductForm,ProductForm1
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import Http404,JsonResponse,HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.core.cache import cache
from django.template.loader import render_to_string
from mail_templated import send_mail
from io import BytesIO

import os
from weasyprint import HTML

from templated_email import send_templated_mail

from django.core.mail import EmailMessage

from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount import providers
from allauth.socialaccount.helpers import complete_social_login
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Error
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter, OAuth2CallbackView, OAuth2LoginView


from .task import *



import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY



# def is_admin(user):
#     return user.is_authenticated and user.is_superuser

from functools import wraps
from django.http import HttpResponseForbidden

def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            # return HttpResponseForbidden("Access denied. You must be a superuser to view this page.")
            return redirect('user-home')
    return _wrapped_view

@superuser_required
@login_required(login_url='login/')
def homePage(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    user = CustomUser.objects.all()
    context = {'products': products,'user':user,'orders':orders}
    return render(request,'index.html',context)

def register_and_login(request):
    try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            name = request.POST['name']
            email = request.POST['email']
        
            try:
                user = CustomUser.objects.create_user(username=username, password=password, name=name, email=email)
                if user is not None:
                    return redirect('login')
                else:
                    return render(request, 'register.html', {'error_message': 'Error logging in after registration'})
            except IntegrityError:
                return render(request, 'register.html', {'error_message': 'Email address is already in use. Please choose another email.'})
        
        return render(request, 'register.html')
    except Exception as e:
        print("error.................................", e)


def login(request):
    # try:
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                print(user.is_superuser)
                if user.is_superuser:
                    auth_login(request, user)
                    return redirect('home')
                else:
                    # return render(request, 'login.html', {'error_message': 'You are not Admin'})
                    auth_login(request, user)
                    return redirect('user-home')
            else:
                return render(request, 'login.html', {'error_message': 'Invalid credentials'})
        else:
            return render(request, 'login.html')
    # except Exception as e:
    #     print(e)


@login_required(login_url='/login/')
def profilePage(request):
    return render(request,'profile.html')

@login_required(login_url='/login/')
def logout_view(request):
    logout(request)
    return redirect('login') 



@login_required(login_url='/login/')
def edit_profile(request, user_id=None):
    error_message = None 
    if user_id is None:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)

    else:
        if request.user.is_superuser:
            user = CustomUser.objects.get(id=user_id)
            profile = user.userprofile
        else:
            return HttpResponse("You don't have permission to edit this user's profile.")
    if request.method == 'POST':
        try:
            about = request.POST.get('about', '')
            name = request.POST.get('fname','')
            profile_pic = request.FILES.get('profile_pic', None)
            job_title = request.POST.get('job_title', '')
            country = request.POST.get('country', '')
            address = request.POST.get('address', '')
            email = request.POST.get('email', '')
            mobile_number = request.POST.get('mobile_number')
            profile.job_title = job_title
            # Update profile fields and save
            profile.about = about
            profile.country = country
            profile.address = address
            profile.mobile_number = mobile_number
            user.email = email
            user.name = name
            user.save()
            if profile_pic:
                profile.profile_pic = profile_pic
            profile.save()
            messages.success(request, "Profile data updated successfully!")

            if user_id is None:
                return redirect('profile')
            
            else:
                return redirect('user-profile',pk=user.id)  

        except IntegrityError as e:
            if 'UNIQUE constraint' in str(e) and 'email' in str(e):
                messages.error(request, "The provided email is already in use....")
            else:
                messages.error(request, "An error occurred while updating the profile.") 
            return redirect('user-profile', pk=user.id)  

    return render(request, 'user_profile.html')


@login_required(login_url='/login/')
def change_password(request):
    try:
        if request.method == 'POST':
            current_password = request.POST.get('password')
            new_password = request.POST.get('newpassword')
            renew_password = request.POST.get('renewpassword')
            
            if request.user.check_password(current_password) and new_password == renew_password:
                request.user.set_password(new_password)
                request.user.save()
                messages.success(request, "Password changed successfully. You have been logged out.")
                logout(request)
                return redirect('login')  
            else:
                messages.error(request, "Password change failed. Please check your inputs....")
            
        return render(request, 'profile.html')
    except Exception as e:
        print(e)

@login_required(login_url='/login/')
def contactPage(request):
    return render(request,'contact.html')

@superuser_required
@login_required(login_url='/login/')
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)

def product_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    if request.method == 'POST':
        form = ProductForm1(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            cache.delete('cached_products')
            return redirect('product-detail', product_id=product_id)
    else:
        form = ProductForm(instance=product)
    context = {'form': form, 'product': product}
    return render(request, 'product_update.html', context)

@superuser_required
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        cache.delete('cached_products')
        return redirect('home')
    return render(request, 'product_delete.html', {'product': product})

@superuser_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            cache.delete('cached_products')
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


@method_decorator(staff_member_required, name='dispatch')
class SuperuserOrderListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'

@method_decorator(staff_member_required, name='dispatch')
class OrderDetailView(DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    
@superuser_required
def change_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status:
            order.status = new_status
            order.save()
    return redirect('admin-order-list')

@superuser_required
def user(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    users = CustomUser.objects.all()
    context = {'products': products,'users':users,'orders':orders}
    return render(request,'user_list.html',context)

# @superuser_required
class UserDetailview(DetailView):
    print("@@@@@@@@@@@@@")
    model = UserProfile
    template_name = 'user_profile.html'
    context_object_name = 'user'

CustomUser = get_user_model()
@login_required
@user_passes_test(lambda user: user.is_superuser)
def custom_user_delete(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    print(user)
    if request.method == 'POST':
        if user.is_superuser:
            messages.error(request, "Cannot delete a superuser.")
        else:
            user.delete()
            messages.success(request, f"User {user.username} has been deleted.")
        return redirect('user') 
    return render(request, 'user_list.html', {'user': user})


@superuser_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'product_category.html', {'categories': categories})

@superuser_required
def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.all()

    category_id = request.GET.get('category')
    selected_category = None

    if category_id:
        products = products.filter(category_id=category_id)
        selected_category = Category.objects.get(id=category_id)

    context = {'products': products, 'categories': categories, 'selected_category': selected_category}
    return render(request, 'product_list.html', context)



def session_try(request):
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1
    context = {
        'num_visits': num_visits,
    }
    return render(request, 'session-try.html', context=context)






@login_required(login_url='/login/')
def user_home(request):
    selected_category_id = request.GET.get('category')
    # products = Product.objects.all()
    # categories = Category.objects.all()
    # Check if the products and categories are in the cache
    products = cache.get('cached_products')
    print("this product from cache")

    categories = cache.get('cached_categories')
    print("this categories from cashe")


    if products is None:
        print("this product from DB")
        products = Product.objects.all()
        cache.set('cached_products', products, 300) 
        print("in dbdbdbdbdbdbdbdb")
    
    if categories is None:
        categories = Category.objects.all()
        print("this categories from DB")
        cache.set('cached_categories', categories, 360)

    if selected_category_id:
        products = products.filter(category__id=selected_category_id)

    context = {
        'products': products,
        'categories': categories,
        'active_page': 'home'
    }

    return render(request, 'shop/index.html', context)



@login_required(login_url='/login/')
def user_product(request):
    selected_category_id = request.GET.get('category')
    # products = Product.objects.all()
    # categories = Category.objects.all()
    products = cache.get('cached_products')
    print("this product from cache")

    categories = cache.get('cached_categories')
    print("this categories from cashe")


    if products is None:
        products = Product.objects.all()
        cache.set('cached_products', products, 300) 
    
    if categories is None:
        categories = Category.objects.all()
        cache.set('cached_categories', categories, 360)

    if selected_category_id:
        products = products.filter(category__id=selected_category_id)

    context = {
        'products': products,
        'categories': categories,
        'active_page': 'product'
    }

    return render(request, 'shop/product.html', context)


@login_required(login_url='/login/')
def quick_view(request, product_id):
    try:
        product = get_object_or_404(Product, pk=product_id)
        product_data = {
            'product_image_url': product.product_image.url,
            'product_name': product.label,  
            'product_price': product.price,
            'product_description': product.description,

        }
        return JsonResponse(product_data)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    


@login_required(login_url='/login/')
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))
        print('Received product_id:', product_id)
        print('Received quantity:', quantity)


        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})

        # Check if the user already has this product in their cart
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)

        # if not created:
        #     # If the item already exists in the cart, update the quantity
        #     cart_item.quantity += quantity
        #     cart_item.save()


        if created:
            # If the item was created (i.e., it's the first time), set the quantity to the provided value
            cart_item.quantity = quantity
        else:
            # If the item already exists in the cart, increment the quantity
            cart_item.quantity += quantity

        # Save the cart item
        cart_item.save()



        cache.delete('cached_cart_items')
        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

@login_required(login_url='/login/')
def cart(request):
    # Check if the cart items are in the cache
    cart_items = cache.get('cached_cart_items')

    if cart_items is None:
        # If not in the cache, query the database to get the cart items
        cart_items = CartItem.objects.filter(user=request.user)

        # Store the cart items queryset in the cache with a 20-second timeout
        cache.set('cached_cart_items', cart_items, 200)

    cart_subtotal = 0
    for cart_item in cart_items:
        cart_subtotal += cart_item.subtotal()
    
    cart_total = cart_subtotal

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
    }
    return render(request, 'shop/cart.html', context)

@login_required(login_url='/login/')
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.remove()  
    cache.delete('cached_cart_items')
    return redirect('cart')



@login_required(login_url='/login/')
def update_cart_item(request, cart_item_id):
    if request.method == 'POST':
        new_quantity = int(request.POST.get('new_quantity'))
        try:
            cart_item = CartItem.objects.get(id=cart_item_id)
            if new_quantity > 0:
                cart_item.quantity = new_quantity
                cart_item.save()
                cache.delete('cached_cart_items')
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': 'Quantity must be greater than zero'})
        except CartItem.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Cart item not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request method'})


@login_required(login_url='/login/')
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items:
        cart_subtotal = 0
        for cart_item in cart_items:
            cart_subtotal += cart_item.subtotal()
        cart_total = cart_subtotal
        context = {
            'cart_items': cart_items,
            'cart_subtotal': cart_subtotal,
            'cart_total': cart_total,
        }

        if request.method == 'POST':
            request.session['checkout_data'] = {
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'mobile_number': request.POST.get('mobile_number'),
                'address': request.POST.get('address'),
                'payment_method': request.POST.get('payment')
            }

            cart_total = cart_subtotal


            payment_method = request.POST.get('payment') 

            if payment_method == 'cod':
                return redirect('success')
            else:
            # Redirect to the create_checkout_session view
                return redirect('checkout_session')

        return render(request, 'shop/checkout.html', context)  # Render the checkout page
    else:
        return redirect('cart')


@login_required(login_url='/login/')
def create_checkout_session(request):
    cart_items = CartItem.objects.filter(user=request.user)
    line_items = []
    for cart_item in cart_items:
        product = cart_item.product
        unit_amount_cents = int(cart_item.product.price * 100)  # Convert to cents

        line_items.append({
            'price_data': {
                'currency': 'inr',  # Adjust currency as needed
                'product_data': {
                    'name': product.label,  # Product name
                },
                'unit_amount': unit_amount_cents,
            },
            'quantity': cart_item.quantity,
        })
    current_domain = request.META['HTTP_HOST']

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=f'http://{current_domain}/success/',
        cancel_url=f'http://{current_domain}/cancel',
        client_reference_id=str(request.user.id),
    )

    # Clear the cart after a successful order
    # CartItem.objects.filter(user=request.user).delete()

    return redirect(session.url, code=303)


@login_required(login_url='/login/')    
def cancel(request):
    return render(request,'shop/cancel.html')


def success(request):
    cart_items = CartItem.objects.filter(user=request.user)
    if cart_items:
        cart_subtotal = 0
        for cart_item in cart_items:
            cart_subtotal += cart_item.subtotal()
            
        cart_total = cart_subtotal
    checkout_data = request.session.get('checkout_data')

    if not checkout_data:
        return HttpResponseBadRequest("Missing session data")
    
    order = Order.objects.create(
    user=request.user,
    name=checkout_data['name'],
    email=checkout_data['email'],
    status='Processing',
    total_amount=cart_total,
    address=checkout_data['address'],
    payment_method = checkout_data['payment_method'],
    mobile_number=checkout_data['mobile_number'],
    payment_done = True
    )

    for cart_item in cart_items:
                order.product.add(cart_item.product)
                
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.product.price  
        )
    # Generate and save the PDF invoice
    # order_id = order.id

    # pdf_response = generate_invoice_pdf(request, order.id)

    cache.delete('cached_cart_items')
    # handel_task.delay()

    # print(order_id,'order_id')

    # send_order_confirmation_email.apply_async(args=[order_id,pdf_response])
    send_order_confirmation_email.delay(order.id)

    context = {
        'latest_order': order,
    }
    CartItem.objects.filter(user=request.user).delete()
    
    return render(request, 'shop/checkout_confirmation.html', context)


def extra(request):
    return render(request,'extra.html')





# def google_login_callback(request):
#     # Handle the Google login callback
#     # This view will be used as the callback URL in your Google API credentials
#     app = SocialApp.objects.get(provider='google')  # Ensure 'google' matches the provider name you configured

#     # Handle the Google OAuth2 callback using allauth's OAuth2CallbackView
#     oauth2_adapter = OAuth2Adapter(app)
#     view = OAuth2CallbackView.as_view(adapter=oauth2_adapter)
#     response = view(request)

#     # Check if there was an error during Google OAuth2 authentication
#     if response.status_code == 400:
#         try:
#             error_message = response.data['error_description']
#         except (KeyError, TypeError):
#             error_message = "An error occurred during Google login."
#         return render(request, 'login.html', {'error_message': error_message})

#     # If successful, complete the social login
#     complete_social_login(request, providers.registry.by_id('google'))
    
#     # Redirect to the desired page after successful login
#     return redirect('home')  # Replace 'home' with the URL name of your choice


from allauth.socialaccount.models import SocialApp, SocialAccount
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import View

class GoogleLoginCallback(View):
    def get(self, request):
        print("request.user",request.user)
        try:
            # Ensure that you have configured the Google social app in the Django admin panel
            social_app = SocialApp.objects.get(provider='google')  # Make sure 'google' matches the provider ID
            print("social_app",social_app)
            social_token = SocialAccount.objects.get(user=request.user, provider='google')
            print("social_token",social_token)

            # You can access the Google access token here: social_token.tokens

            # Implement your own logic here, e.g., check user's email and grant permissions accordingly

            auth_login(request, request.user)
            return HttpResponseRedirect(reverse('user-home'))  # Redirect to user's home page after successful login
        except SocialApp.DoesNotExist:
            return render(request, 'error.html', {'error_message': 'Google login is not configured.'})
        except OAuth2Error:
            return render(request, 'error.html', {'error_message': 'Error logging in with Google.'})
        



# def send_custom_email(request):
#     subject = 'Hello, Django Email Template'
#     from_email = 'premal@moontechnolabs.com'
#     recipient_list = ['premal@moontechnolabs.com']

#     send_mail(
#         template_name='shop/email_template.html', 
#         from_email=from_email,
#         recipient_list=recipient_list,

 
#         context={
#             'greeting': 'Hi there!',
#             'message': 'This is an email sent from a template in Django.',
#         },
#         subject=subject,
#     )
    
    
# def send_order_confirmation_email(request):
#     subject = 'Hello, Django Email Template'
#     from_email = 'premal@moontechnolabs.com'
#     recipient_list = ['premal@moontechnolabs.com']
#     message_body = 'This is an email sent from a template in Django.'

#     # Create an EmailMessage instance
#     email_message = EmailMessage(
#         subject,
#         message_body,
#         from_email,
#         recipient_list,
#     )

#     # Send the email
#     email_message.send()

#     # Pass the message body as a context variable to the template
#     context = {'message_body': message_body}

#     # Render the email_template.html template with the context
#     return render(request, 'shop/email_template.html', context)    


# def send_order_confirmation_email(request,order):
#     # subject = f'Order Confirmation - Order #{order.order_number}'
#     subject = 'Order Confirmation' 
#     from_email = 'premal@moontechnolabs.com' 
#     print("order email...............",order.email) # Replace with your email
#     # print("this is order",order.product.label)
#     recipient_list = [order.email]

#     # Create the email message body with order details
#     message_body = f'Thank you for placing an order with us.\n\n'
#     message_body += f'Order Number: {order.id}\n'
#     message_body += f'Customer: {order.name}\n'
#     message_body += f'Address: {order.address}\n'
#     message_body += f'Total Amount: ${order.total_amount}\n'
#     message_body += 'Order Details:\n'

#     # # You can iterate over order items
#     for item in order.orderitem_set.all():
#         message_body += f'- {item.product.label}: ${item.price} x {item.quantity}\n'

#     # Create an EmailMessage instance
#     email_message = EmailMessage(
#         subject,
#         message_body,
#         from_email,
#         recipient_list,
#     )
#     file_path = '/home/premal/Documents/Django_Project (copy)/my_project/static/eshop/images/monkey-3703230_640.jpg'  # Replace with the actual file path
#     email_message.attach_file(file_path)
#     # Send the email
#     email_message.send()



###

# def send_order_confirmation_email(request, order,pdf_response):
#     subject = f'Order Confirmation - Order #{order.id}'
#     from_email = 'your-email@example.com'  # Replace with your email
#     recipient_list = [order.email]

#     # Create a context dictionary with dynamic data for the template
#     context = {
#         'customer_name': order.name,
#         'order_number': order.id,
#         'shipping_address': order.address,
#         'total_amount': order.total_amount,
#         # Add more dynamic data as needed
#     }

#     # Render the email template as a string
#     email_content = render_to_string('shop/order_confirmation_email.html', context)

#     # Create an EmailMessage instance
#     email_message = EmailMessage(
#         subject,
#         email_content,
#         from_email,
#         recipient_list,
#     )

#     # file_path = '/home/premal/Documents/Django_Project (copy)/my_project/static/eshop/images/monkey-3703230_640.jpg'  # Replace with the actual file path
#     # email_message.attach_file(file_path)

#     file_name = f'invoice_{order.id}.pdf'
#     email_message.attach(file_name, pdf_response.getvalue(), 'application/pdf')

#     email_message.content_subtype = 'html'

#     # Send the email
#     email_message.send()

####
from django.utils.html import strip_tags 
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

# def generate_invoice_pdf(request, order_id):
#     try:
#         order = Order.objects.get(pk=order_id)

#         # Create a PDF document
#         buffer = BytesIO()
#         doc = SimpleDocTemplate(buffer, pagesize=letter)

#         # Create a list of flowable elements for the PDF content
#         elements = []

#         # Create a style for the content
#         styles = getSampleStyleSheet()
#         style = styles['Normal']

#         # Create the HTML content using the HTML template
#         invoice_content = render_to_string('shop/invoice_template.html', {'order': order})

#         # Convert the HTML content to flowable elements
#         html_content = Paragraph(invoice_content, style)
#         elements.append(html_content)

#         # Build the PDF document with the flowable elements
#         doc.build(elements)

#         # Get the value of the BytesIO buffer and return it as a PDF file
#         pdf = buffer.getvalue()
#         buffer.close()

#         # Create an HttpResponse with the PDF content for download
#         response = HttpResponse(content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'
#         response.write(pdf)

#         return response
#     except Order.DoesNotExist:
#         # Handle the case where the order does not exist
#         return HttpResponseBadRequest("Order not found")

# def generate_invoice_pdf(request, order_id):
#     try:
#         order = Order.objects.get(pk=order_id)
#         print("order is",order)

#         # Create HTML content from the template
#         html_content = render_to_string('shop/invoice_template.html', {'order': order})

#         # Generate PDF using WeasyPrint
#         pdf_file = HTML(string=html_content).write_pdf()

#         # Define the folder path where you want to store the PDF invoices
#         invoice_folder = os.path.join(settings.MEDIA_ROOT, 'invoices')
#          # Ensure the invoices folder exists; create it if it doesn't
#         os.makedirs(invoice_folder, exist_ok=True)

#         file_name = f'invoice_{order_id}.pdf'
#         file_path = os.path.join(invoice_folder, file_name)

#         # Save the PDF to the specified folder
#         with open(file_path, 'wb') as pdf_file:
#             pdf_file.write(pdf_file)

#         # Create an HttpResponse with the PDF content for download
#         response = HttpResponse(pdf_file, content_type='application/pdf')
#         response['Content-Disposition'] = f'attachment; filename={file_name}'

#         return response
#     except Order.DoesNotExist:
#         return HttpResponseBadRequest("Order not found")



def generate_invoice_pdf(request, order_id):
    try:
        order = Order.objects.get(pk=order_id)
        print("order is", order)

        # Create HTML content from the template
        html_content = render_to_string('shop/invoice_template.html', {'order': order})
        presentational_hints = True
        # Generate PDF using WeasyPrint
        pdf_bytes = HTML(string=html_content, base_url=settings.STATIC_URL).write_pdf(presentational_hints=presentational_hints)
        # Define the folder path where you want to store the PDF invoices
        invoice_folder = os.path.join(settings.MEDIA_ROOT, 'invoices')

        # Ensure the invoices folder exists; create it if it doesn't
        os.makedirs(invoice_folder, exist_ok=True)

        # Define the file path for the PDF (e.g., /media/invoices/invoice_123.pdf)
        file_name = f'invoice_{order_id}.pdf'
        file_path = os.path.join(invoice_folder, file_name)

        # Save the PDF content to the specified file
        with open(file_path, 'wb') as pdf_file:
            pdf_file.write(pdf_bytes)

        # Create an HttpResponse with the PDF content for download
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename={file_name}'

        return response
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")
    




def send_email_reminders(request):
    print("this is from crone job..................")