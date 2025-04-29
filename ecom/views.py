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

# Helper function to get or create single category
def get_single_category(name, description):
    # First try to get the category
    categories = Category.objects.filter(name=name)
    if categories.exists():
        # If multiple categories exist, use the first one and delete others
        if categories.count() > 1:
            main_category = categories.first()
            # Delete other duplicates
            categories.exclude(id=main_category.id).delete()
            return main_category
        return categories.first()
    else:
        # If no category exists, create new one
        return Category.objects.create(name=name, description=description)

# Collection categories
coll = Product.objects.all()

try:
    # Get fashion categories
    category_men = get_single_category("men", "Men's Fashion")
    category_women = get_single_category("Women", "Women's Fashion")
    category_acc = get_single_category("accessories", "Fashion Accessories")

    # Get medicine categories
    category_otc = get_single_category("medicines", "Over the counter medicines")
    category_firstaid = get_single_category("firstaid", "First aid supplies")
    category_wellness = get_single_category("wellness", "Wellness and health products")

    # Filter products
    men = Product.objects.filter(category=category_men)
    women = Product.objects.filter(category=category_women)
    acc = Product.objects.filter(category=category_acc)
    otcMed = Product.objects.filter(category=category_otc)
    firstAid = Product.objects.filter(category=category_firstaid)
    wellness = Product.objects.filter(category=category_wellness)

except Exception as e:
    print(f"Error handling categories: {str(e)}")
    # Set default empty querysets in case of error
    men = women = acc = otcMed = firstAid = wellness = Product.objects.none()

def collection(request):
    return render(request,'ecom/collection.html',{"menColl":men,"womenColl":women,"accColl":acc})

@login_required(login_url='/loginpg/')
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
        name=request.POST['name']
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


@login_required(login_url='/loginpg/')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')

@login_required(login_url='/loginpg/')
def remove_from_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, cart=cart, product=product)
    cart_item.delete()
    return redirect('cart')

# views.py
from django.db.models import Sum, F

@login_required(login_url='/loginpg/')
def cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    
    total_price = cart_items.aggregate(total=Sum(F('quantity') * F('product__price')))['total'] or 0
    
    return render(request, 'ecom/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price
    })

# FOR ORDERS

@login_required(login_url='/loginpg/')
def orders(request):
    # Retrieve orders associated with the current user
    user_orders = Order.objects.filter(user=request.user)
    return render(request, "ecom/orders.html", {'user_orders': user_orders})

def order_it(request,product_id):
	product = get_object_or_404(Product, pk=product_id)
	return render(request,'ecom/order.html',{'product': product})

@login_required(login_url='/loginpg/')
def cart_checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.cartitem_set.all()
    total_price = sum(item.quantity * item.product.price for item in cart_items)
    
    return render(request, 'ecom/order.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'is_cart_checkout': True
    })

@login_required(login_url='/loginpg/')
def place_order(request):
    if request.method == 'POST':
        cart = get_object_or_404(Cart, user=request.user)
        cart_items = cart.cartitem_set.all()
        
        # Create address instance
        address_instance = Address.objects.create(
            user=request.user,
            address_line1=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
            zip_code=request.POST.get('postal_code'),
            country=request.POST.get('country')
        )

        # Create order instance
        total_price = cart_items.aggregate(
            total=Sum(F('quantity') * F('product__price'))
        )['total'] or 0
        
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            status='Pending'
        )

        # Add all products from cart to order
        for cart_item in cart_items:
            order.products.add(cart_item.product)

        # Create payment record
        Payment.objects.create(
            order=order,
            payment_method='Cash on delivery',
            amount_paid=total_price,
            transaction_id='',
            status='Pending'
        )

        # Clear the cart
        cart_items.delete()

        messages.success(request, 'Order placed successfully!')
        return redirect('orders')

    return redirect('cart')

def medicine(request):
    try:
        # Get the medicines category
        medicines_category = Category.objects.get(name="medicines")
        # Get all products in the medicines category
        medicine_products = Product.objects.filter(category=medicines_category)
        
        return render(request, 'ecom/medicine.html', {
            "otcMed": medicine_products,
        })
    except Category.DoesNotExist:
        # Handle case where category doesn't exist
        return render(request, 'ecom/medicine.html', {
            "otcMed": [],
        })

def wellness(request):
    try:
        wellness_category = Category.objects.get(name="wellness")
        wellness_products = Product.objects.filter(category=wellness_category)
        return render(request, 'ecom/wellness.html', {
            "wellness": wellness_products,
        })
    except Category.DoesNotExist:
        return render(request, 'ecom/wellness.html', {
            "wellness": [],
        })

def firstaid(request):
    try:
        firstaid_category = Category.objects.get(name="firstaid")
        firstaid_products = Product.objects.filter(category=firstaid_category)
        return render(request, 'ecom/firstaid.html', {
            "firstAid": firstaid_products,
        })
    except Category.DoesNotExist:
        return render(request, 'ecom/firstaid.html', {
            "firstAid": [],
        })

def account(request):
    return render(request,'ecom/account.html')

def healthcare(request):
    try:
        medicines = Product.objects.filter(category__name="medicines")[:4]
        firstaid = Product.objects.filter(category__name="firstaid")[:4]
        wellness = Product.objects.filter(category__name="wellness")[:4]
        
        return render(request, 'ecom/healthcare.html', {
            "medicines": medicines,
            "firstaid": firstaid,
            "wellness": wellness,
        })
    except Exception as e:
        print(f"Error: {str(e)}")
        return render(request, 'ecom/healthcare.html', {
            "medicines": [],
            "firstaid": [],
            "wellness": [],
        })

@login_required(login_url='/loginpg/')
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    address = Address.objects.filter(user=request.user).last()
    payment = Payment.objects.filter(order=order).first()
    
    return render(request, 'ecom/orderdetails.html', {
        'order': order,
        'address': address,
        'payment': payment
    })


