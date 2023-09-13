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

import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY

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



# @login_required(login_url='/login/')
# def edit_profile(request):
#     try:
#         user = request.user 
#         print(user.email)
#         profile, created = UserProfile.objects.get_or_create(user=user)
#         error_message = None 
#         if request.method == 'POST':
#             try:
#                 about = request.POST.get('about', '')
#                 profile_pic = request.FILES.get('profile_pic', None)
#                 job_title = request.POST.get('job_title', '')
#                 country = request.POST.get('country', '')
#                 address = request.POST.get('address', '')
#                 email = request.POST.get('email', '')
#                 mobile_number = request.POST.get('mobile_number')
#                 profile.job_title = job_title
#                 # Update profile fields and save
#                 profile.about = about
#                 profile.country = country
#                 profile.address = address
#                 profile.mobile_number = mobile_number
#                 user.email = email
#                 user.save()
#                 if profile_pic:
#                     profile.profile_pic = profile_pic
#                 profile.save()
#                 return redirect('profile')  
#             except IntegrityError as e:
#                 if 'UNIQUE constraint' in str(e) and 'email' in str(e):
#                     error_message = "The provided email is already in use."
#                 else:
#                     error_message = "An error occurred while updating the profile." 
                
#         return render(request, 'profile.html', {'error_message': error_message})
#     except Exception as e:
#         print(e)





# @login_required(login_url='/login/')
# def edit_profile(request, user_id=None):
#     error_message = None 
#     if user_id is None:
#         user = request.user
#         profile, created = UserProfile.objects.get_or_create(user=user)
#         print("this is logged user...............")
#     else:
#         if request.user.is_superuser:
#             user = CustomUser.objects.get(id=user_id)
#             profile = user.userprofile
#             print("this is by admin..............")
#         else:
#             return HttpResponse("You don't have permission to edit this user's profile.")
#         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
#     if request.method == 'POST':
#         try:
#             about = request.POST.get('about', '')
#             profile_pic = request.FILES.get('profile_pic', None)
#             job_title = request.POST.get('job_title', '')
#             country = request.POST.get('country', '')
#             address = request.POST.get('address', '')
#             email = request.POST.get('email', '')
#             mobile_number = request.POST.get('mobile_number')
            
#             if email != user.email and CustomUser.objects.filter(email=email).exclude(id=user.id).exists():
#                 messages.error(request, "The provided email is already in use.")
#             else:
#                 profile.job_title = job_title
#                 # Update profile fields and save
#                 profile.about = about
#                 profile.country = country
#                 profile.address = address
#                 profile.mobile_number = mobile_number
#                 user.email = email
#                 user.save()
#                 if profile_pic:
#                     profile.profile_pic = profile_pic
#                 profile.save()
#                 print(user_id)
#                 if user_id is None:
#                     print("innnnn")
#                     messages.success(request, "Profile updated successfully.")
#                     return redirect('profile')
#                 else:
#                     print('out.......')
#                     messages.success(request, "Profile updated successfully.")
#                     return redirect('user-profile', pk=user.id)  

#         except IntegrityError as e:
#             if 'UNIQUE constraint' in str(e) and 'email' in str(e):
#                 messages.error(request, "The provided email is already in use.")
#             else:
#                 messages.error(request, "An error occurred while updating the profile.") 
#         return redirect('user-profile', pk=user.id)  
            
    
#     return render(request, 'user_profile.html')

@login_required(login_url='/login/')
def edit_profile(request, user_id=None):
    error_message = None 
    if user_id is None:
        user = request.user
        profile, created = UserProfile.objects.get_or_create(user=user)

        print("this is logged user...............")
    else:
        if request.user.is_superuser:
            user = CustomUser.objects.get(id=user_id)
            profile = user.userprofile
            print("this is by admin..............")
        else:
            return HttpResponse("You don't have permission to edit this user's profile.")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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

            print(user_id)
            if user_id is None:
                print("innnnn")
                return redirect('profile')
            
            else:
                print('out.......')
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

@login_required(login_url='/login/')
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    context = {'product': product}
    return render(request, 'product_detail.html', context)

def product_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    print(product)
    if request.method == 'POST':
        form = ProductForm1(request.POST, instance=product)
        if form.is_valid():
            form.save()
            print("11111111111")
            return redirect('product-detail', product_id=product_id)
    else:
        # print("innnn",form)
        form = ProductForm(instance=product)
    context = {'form': form, 'product': product}
    print('121212')
    return render(request, 'product_update.html', context)


def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        product.delete()
        return redirect('home')
    return render(request, 'product_delete.html', {'product': product})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})


class OrderListView(ListView):
    model = Order
    template_name = 'order_list.html'
    context_object_name = 'orders'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

def change_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('new_status')
        if new_status:
            order.status = new_status
            order.save()
    return redirect('admin-order-list')

def user(request):
    products = Product.objects.all()
    orders = Order.objects.all()
    users = CustomUser.objects.all()
    context = {'products': products,'users':users,'orders':orders}
    return render(request,'user_list.html',context)

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


# def product_list(request):
#     products = Product.objects.all()  
#     context = {'products': products}
#     return render(request, 'product_list.html', context)

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'product_category.html', {'categories': categories})

# def product_list_by_category(request, category_id):
#     category = Category.objects.get(id=category_id)
#     products = Product.objects.filter(category=category)
#     print(request)
#     print(products)
#     print(category)
#     return render(request, 'product_list.html', {'category': category, 'products': products})


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
    print(request)
    context = {
        'num_visits': num_visits,
    }
    return render(request, 'session-try.html', context=context)





# def user_home(request):
#     selected_category_id = request.GET.get('category')

#     products = Product.objects.all()
#     categories = Category.objects.all()

#     if selected_category_id:
#         products = Product.objects.filter(category__id=selected_category_id)
#     return render(request, 'shop/index.html', {'products': products, 'categories': categories})



# def user_home(request):
#     selected_category_id = request.GET.get('category')

#     products = Product.objects.all()
#     categories = Category.objects.all()

#     if selected_category_id:
#         products = Product.objects.filter(category__id=selected_category_id)

#     product_id = request.GET.get('product_id')

#     if product_id:
#         product = Product.objects.get(id=product_id)
#         context = {
#             'products': products,
#             'categories': categories,
#             'product': product,
#         }
#     else:
#         context = {
#             'products': products,
#             'categories': categories,
#         }

#     return render(request, 'shop/index.html', context)


# def user_product(request):
#     selected_category_id = request.GET.get('category')
    
#     products = Product.objects.all()
#     categories = Category.objects.all()
    
#     if selected_category_id:
#         products = Product.objects.filter(category__id=selected_category_id)
        
#     return render(request, 'shop/product.html', {'products': products, 'categories': categories})







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
    



def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        print('Received product_id:', product_id)
        quantity = int(request.POST.get('quantity', 1))
        print('quantity.....1',quantity)

        try:
            product = Product.objects.get(id=product_id)
            print("product is",product)
        except Product.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Product not found'})

        # Check if the user already has this product in their cart
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product,quantity=quantity)

        if not created:
            # If the item already exists in the cart, update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return JsonResponse({'success': True, 'message': 'Product added to cart'})
    else:
        return JsonResponse({'success': False, 'message': 'Invalid request method'})
    


def cart(request):
    cart_subtotal = 0 
    cart_items = CartItem.objects.filter(user=request.user)
    print('items:',cart_items)
    print(request.user)
    for cart_item in cart_items:
        cart_subtotal += cart_item.subtotal()
    cart_total = cart_subtotal
    print("cart_total",cart_total)
    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'cart_total': cart_total,
    }
    return render(request, 'shop/cart.html',context)


def remove_cart_item(request, cart_item_id):
    cart_item = get_object_or_404(CartItem, id=cart_item_id, user=request.user)
    cart_item.remove()  
    return redirect('cart')




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
            print("innnnnnnn")
            name = request.POST.get('name')
            email = request.POST.get('email')
            mobile_number = request.POST.get('mobile_number')
            address = request.POST.get('address')
            cart_total = cart_subtotal

            order = Order.objects.create(
                user=request.user,
                name=name,
                email=email,
                status='processing',
                total_amount=cart_total,
                address=address,
                mobile_number=mobile_number
            )
            for cart_item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price  # Set the price here or retrieve it from elsewhere
                )
            payment_method = request.POST.get('payment') 
            print("payment methiod is", payment_method)

            if payment_method == 'cash':
                print("in cash")
                try:
                    latest_order = Order.objects.filter(user=request.user).latest('date')
                except Order.DoesNotExist:
                    return HttpResponseBadRequest("No orders found for the current user")
                CartItem.objects.filter(user=request.user).delete()

                return redirect('success', order_id=latest_order.id)
            else:
            # Redirect to the create_checkout_session view
                return redirect('checkout_session')

        return render(request, 'shop/checkout.html', context)  # Render the checkout page
    else:
        return redirect('cart')

def create_checkout_session(request):
    try:
        latest_order = Order.objects.filter(user=request.user).latest('date')
    except Order.DoesNotExist:
        return HttpResponseBadRequest("No orders found for the current user")
    cart_items = CartItem.objects.filter(user=request.user)
    line_items = []
    for cart_item in cart_items:
        product = cart_item.product
        unit_amount_cents = int(cart_item.subtotal() * 100)  # Convert to cents

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
        success_url=f'http://{current_domain}/success/{latest_order.id}',
        cancel_url=f'http://{current_domain}/cancel',
    )

    # Clear the cart after a successful order
    CartItem.objects.filter(user=request.user).delete()

    return redirect(session.url, code=303)


# @login_required

def success(request,order_id):
    # order_id = request.GET.get('order_id')
    # print("order_id..",order_id)
    # if not order_id:
    #     return HttpResponseBadRequest("Missing order_id parameter")
    try:
        latest_order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return HttpResponseBadRequest("Order not found")

    context = {
        'latest_order': latest_order,
    }
    return render(request, 'shop/checkout_confirmation.html', context)


def cancel(request):
    return render(request,'shop/cancel.html')



