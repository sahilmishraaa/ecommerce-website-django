from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Contact)
admin.site.register(CartItem)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Order)
admin.site.register(Payment)