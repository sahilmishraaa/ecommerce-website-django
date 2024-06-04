from django.shortcuts import render,redirect, get_object_or_404, HttpResponse
from .models import *
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    return render(request,'ecom/index.html')

# Collection
coll = Product.objects.all()
category_men = Category.objects.get(name="men")
category_women = Category.objects.get(name="Women")
category_acc = Category.objects.get(name="accessories")

men=Product.objects.filter(category=category_men)
women=Product.objects.filter(category=category_women)
acc=Product.objects.filter(category=category_acc)

def collection(request):
    return render(request,'ecom/collection.html',{"menColl":men,"womenColl":women,"accColl":acc})

def customercare(request):
    if request.method=="POST":
        name=request.POST['name']
        email=request.POST['email']
        subject=request.POST['subject']
        content=request.POST['content']
        print(name,email,subject,content)
        contact = Contact(name=name,email=email,subject=subject,content=content)
        contact.save()

    return render(request,'ecom/CCare.html')

def loginpg(request):
    return render(request,'ecom/login.html')

def signup(request):
    return render(request,'ecom/signup.html')


def loginmanage(request):
    if request.method=='POST':
        loginusername = request.POST['loginusername']
        loginpassword = request.POST['loginpassword']
        user = authenticate(username=loginusername,password=loginpassword)

        if user is not None:
            login(request,user)
            messages.error(request, "Document deleted.")
            return redirect('home')
        else :
            return HttpResponse('Invalid Credentials')

def logoutmanage(request):
    logout(request)
    return redirect('home')


def lookbook(request):
    return render(request,'ecom/lookbook.html',{"items":coll})

def product(request,product_id):
    product = get_object_or_404(Product,pk=product_id)
    return render(request,'ecom/product.html',{"product":product})
 

def signupmanage(request):
    if request.method=='POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']


        #Error checks
        if len(username)>15:
            return HttpResponse('Username must be less than 15 characters.')
        
        if not username.isalnum():
            return HttpResponse('User name must be alphanumeric.')
        
        if password!=cpassword:
            return HttpResponse('Passwords Do Not Match')

        #Create User
        myuser = User.objects.create_user(username,email,password)
        myuser.save()
        # creating cart for the user
        cart = Cart(user=myuser)
        cart.save()
        messages.success(request,'Your Account Has Been Created.')
        return redirect('home')
    else:
        return HttpResponse('Error 404 Not Found')

# views.py
from django.shortcuts import get_object_or_404, redirect, render
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')

# views.py
from django.db.models import Sum, F

@login_required
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    
    total_price = cart_items.aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0
    
    return render(request, 'ecom/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    })


