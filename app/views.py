from django.shortcuts import render,redirect
from django.contrib.auth import get_user_model
from .models import CustomUser,UserProfile,Product
from django.contrib.auth import authenticate
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.db import IntegrityError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .forms import ProductForm

@login_required(login_url='login/')
def homePage(request):
    products = Product.objects.all()
    user = CustomUser.objects.all()
    context = {'products': products,'user':user}
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
                    return render(request, 'login.html', {'error_message': 'You are not Admin'})
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
def edit_profile(request):
    try:
        user = request.user
        print(user.email)
        profile, created = UserProfile.objects.get_or_create(user=user)
        error_message = None 
        if request.method == 'POST':
            try:
                about = request.POST.get('about', '')
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
                user.save()
                if profile_pic:
                    profile.profile_pic = profile_pic
                profile.save()
                return redirect('profile')  
            except IntegrityError as e:
                if 'UNIQUE constraint' in str(e) and 'email' in str(e):
                    error_message = "The provided email is already in use."
                else:
                    error_message = "An error occurred while updating the profile." 
                
        return render(request, 'profile.html', {'error_message': error_message})
    except Exception as e:
        print(e)

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
                messages.error(request, "Password change failed. Please check your inputs.")
            
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