from django.contrib import admin
from api.models import Order, OrderItem, User, Product

# Register your models here.

#here we attach the OrderItem model to the Order model in the admin interface
class OrderItemInline(admin.TabularInline):
    model = OrderItem

#here we allow the user to manage OrderItems directly from the Order admin page like creating, editing, and deleting them
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        OrderItemInline
    ]
    
# here we register the Order model with the admin site using the OrderAdmin class
admin.site.register(Order, OrderAdmin)
admin.site.register(User)
admin.site.register(Product)