from django.db import models
from django.contrib.auth.models import User


class Admin(models.Model):
    user= models.OneToOneField(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=20)
    image=models.ImageField(upload_to='admins')
    mobile=models.CharField(max_length=10)

    def __str__(self):
        return self.user.username

# Create your models here.
class Customer(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    full_name=models.CharField(max_length=20)
    address=models.CharField(max_length=20)
    joined_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class Category(models.Model):
    title=models.CharField(max_length=20)
    slug=models.SlugField(unique=True)

    def __str__(self):
        return self.title
    

class Product(models.Model):
    title=models.CharField(max_length=20)
    slug=models.SlugField(unique=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    image=models.ImageField(upload_to='products')
    marked_price=models.PositiveIntegerField()
    selling_price=models.PositiveIntegerField()
    description=models.CharField(max_length=50)
    warrenty=models.CharField(max_length=30,null=True, blank=True)
    return_policy=models.CharField(max_length=20,null=True,blank=True)
    view_count=models.PositiveIntegerField(default=0)    

    def __str__(self):
        return self.title
    

class Cart(models.Model):
    customer=models.ForeignKey(Customer,on_delete=models.SET_NULL,null=True, blank=True)
    total=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Cart: " + str(self.id)
    

class CartProduct(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE)
    Product=models.ForeignKey(Product,on_delete=models.CASCADE)
    rate=models.PositiveIntegerField()
    quantity=models.PositiveIntegerField()
    subtotal=models.PositiveIntegerField()

    def __str__(self):
        return 'Cart :'+ str(self.cart.id) + "CartProduct :" + str(self.id)  



ORDER_STATUS=(
    ('ORDERRECEIVED ', 'ORDER_RECEIVED'),
    ('ORDER PROCESSING ', 'ORDER_PROCESSING'),
    ('ON THE WAY ', 'ON THE WAY'),
    ('ORDER COMPLETED ', 'ORDER_COMPLETED'),
    ('ORDER CANCELED', 'ORDER_CANCELED'),
    
)      


class Order(models.Model):
    cart=models.OneToOneField(Cart,on_delete=models.CASCADE)
    order_by=models.CharField(max_length=20)
    shipping_address=models.CharField(max_length=20)
    mobile=models.CharField(max_length=10)
    email=models.EmailField(null=True ,blank=True)
    subtotal=models.PositiveIntegerField()
    discount=models.PositiveIntegerField()
    total=models.PositiveIntegerField()
    order_status=models.CharField(max_length=30,choices=ORDER_STATUS)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Order :' + str(self.id)
