from django.shortcuts import render,redirect,HttpResponse
from django.contrib.auth import get_user_model
from .models import CustomUser,UserProfile,Product,Order,Category
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
from django.http import Http404,JsonResponse

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