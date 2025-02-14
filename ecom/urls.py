from django.urls import path
from .views import *

urlpatterns=[
    path('',home,name ='home'),
    path('home/',home,name ='home'),
    path('collection/',collection,name ='collection'),
    path('customercare/',customercare,name ='customercare'),
    path('product/<int:product_id>/',product,name='product'),
    path('loginpg/',loginpg,name='loginpg'),
    path('signup/',signup,name='signup'),
    path('lookbook/',lookbook,name='lookbook'),
    path('signupmanage/',signupmanage,name='signupmanage'),
    path('loginmanage/',loginmanage,name='loginmanage'),
    path('logoutmanage/',logoutmanage,name='logoutmanage'),
    path('cart/', cart, name='cart'),
    path('cart/add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),

]