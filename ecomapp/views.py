from django.shortcuts import render
from django.views.generic import TemplateView
from .models import *

# Create your views here.
class Homeview(TemplateView):
    template_name='home.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['product_list']=Product.objects.all()
        return context
    

class AllProductView(TemplateView):
    template_name='allproduct.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['allcategories']=Category.objects.all()
        return context  

class ProductDetailView(TemplateView):
    template_name='productdetail.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        url_slug=self.kwargs['slug']
        product=Product.objects.get(slug=url_slug)
        context['product']=product
        return context


class AddToCartView(TemplateView):
    template_name='addtocart.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        # get product id from request url
        product_id=self.kwargs['pro_id']

        #get product from product id
        product_obj=Product.objects.get(id=product_id)

        #check cart exist or not
        cart_id=self.request.session.get('cart_id',None)

        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            product_in_cart=cart_obj.cartproduct_set.filter(Product=product_obj)

            if product_in_cart.exists():
                cartproduct=product_in_cart.last()
                cartproduct.quantity+=1
                cartproduct.subtotal+=product_obj.selling_price
                cartproduct.save()
                cart_obj.total+=product_obj.selling_price
                cart_obj.save()

            else:
                cartproduct=CartProduct.objects.create(
                    cart=cart_obj,Product=product_obj,rate=product_obj.selling_price,quantity=1,
                subtotal=product_obj.selling_price)
                cart_obj.total+=product_obj.selling_price
                cart_obj.save()
            print('old cart')

        else:
            cart_obj=Cart.objects.create(total=0)
            self.request.session['cart_id']=cart_obj.id 
            print('new cart')   

class MyCartView(TemplateView):
    template_name='mycart.html' 

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs) 
        cart_id=self.request.session.get('cart_id',None)   
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
        else:
            cart=None
        context['cart']=cart     
        return context      


class Aboutview(TemplateView):
    template_name='about.html'


class Contactview(TemplateView):
    template_name='contact.html'    
    