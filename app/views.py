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
    try:
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
        return render(request, 'login.html')
    except Exception as e:
        print(e)


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
        return redirect('home')
    return render(request, 'product_delete.html', {'product': product})

@superuser_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
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
    products = Product.objects.all()
    categories = Category.objects.all()

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
    products = Product.objects.all()
    categories = Category.objects.all()

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
            'product_name': product.label,  # Use the label field as the name
            'product_price': product.price,
            'product_description': product.description,
            # You might need to adjust the following fields based on your model structure
            'product_size': '',  # Add the appropriate field from your model
            'product_color': '',  # Add the appropriate field from your model
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

        if not created:
            # If the item already exists in the cart, update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    

@login_required(login_url='/login/')
def cart(request):
    cart_subtotal = 0 
    cart_items = CartItem.objects.filter(user=request.user)
    for cart_item in cart_items:
        cart_subtotal += cart_item.subtotal()
    cart_total = cart_subtotal
    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
    }
    return render(request, 'shop/cart.html',context)

@login_required(login_url='/login/')
def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.remove()  
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



# @csrf_exempt  # Ensure CSRF protection is disabled for this view
# def webhook(request):
#     print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#     payload = request.body
#     sig_header = request.META['HTTP_STRIPE_SIGNATURE']
#     webhook_secret_key = settings.STRIPE_WEBHOOK_SECRET
#     # Verify the event data using your Stripe secret key
#     try:
#         event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret_key)
#     except ValueError as e:
#         # Invalid payload
#         return JsonResponse({'error': str(e)}, status=400)
#     except stripe.error.SignatureVerificationError as e:
#         # Invalid signature
#         return JsonResponse({'error': str(e)}, status=400)

#     if event.type == 'checkout.session.completed':
#         # Payment was successful, create the order and clear the cart
#         session = event.data.object
        # order = create_order(session)  # Implement this function to create the order
#         print("session..............",session)

#         return JsonResponse({'status': 'success'})
#     else:
#         print('this is for not success')

#     return JsonResponse({'status': 'ignored'})


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
    context = {
        'latest_order': order,
    }
    CartItem.objects.filter(user=request.user).delete()
    
    return render(request, 'shop/checkout_confirmation.html', context)


def extra(request):
    return render(request,'extra.html')