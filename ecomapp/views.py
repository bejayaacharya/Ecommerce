from django.shortcuts import render,redirect
from django.views.generic import  View,TemplateView,CreateView,FormView,FormView,DetailView,ListView
from .models import *
from django.urls import reverse_lazy
from .forms import *
from django.contrib.auth import authenticate,login,logout
from django.core.paginator import Paginator

# Create your views here.

class EcomMixin(object):
    def dispatch(self, request,*args,**kwargs):
        cart_id=request.session.get('cart_id')
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer=request.user.customer
                cart_obj.save()
        return super().dispatch(request,*args,**kwargs)        



class Homeview(EcomMixin,TemplateView):
    template_name='home.html'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        all_products=Product.objects.all()
        paginator=Paginator(all_products,6)
        page_number=self.request.GET.get('page')
        product_list=paginator.get_page(page_number)
        context['product_list']=product_list
        return context
    

class AllProductView(EcomMixin,TemplateView):
    template_name='allproduct.html'

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        context['allcategories']=Category.objects.all()
        return context  

class ProductDetailView(EcomMixin,TemplateView):
    template_name='productdetail.html'


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        url_slug=self.kwargs['slug']
        product=Product.objects.get(slug=url_slug)
        context['product']=product
        return context


class AddToCartView(EcomMixin,TemplateView):
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

class ManageCart(EcomMixin,View):
    def get(self,request,*args,**kwargs):
        print('this is manage cart section')
        cp_id=self.kwargs['cp_id']
        action=request.GET.get('action')
        print(cp_id,action)
        cp_obj=CartProduct.objects.get(id=cp_id)
        cart_obj=cp_obj.cart

        if action=='inc':
            cp_obj.quantity+=1
            cp_obj.subtotal+=cp_obj.rate
            cp_obj.save()
            cart_obj.total+=cp_obj.rate
            cart_obj.save()

        elif action=='dcr':
            cp_obj.quantity-=1
            cp_obj.subtotal-=cp_obj.rate
            cp_obj.save()
            cart_obj.total-=cp_obj.rate
            cart_obj.save()

            if cp_obj.quantity==0:
                cp_obj.delete()

            pass

        elif action=='rmv':
            cart_obj.total-=cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()

            pass

        else:
            pass         

    

        return redirect('ecomapp:mycart')
    

class  EmptyCartView(EcomMixin,View):
    def get(self, request,*args,**kwargs):
        cart_id=request.session.get('cart_id',None)
        if cart_id:
            cart=Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total=0
            cart.save()
        return redirect('ecomapp:mycart')    


class MyCartView(EcomMixin,TemplateView):
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

class CheckOutView(EcomMixin,CreateView):
    template_name='checkout.html'
    form_class=CheckOutForm
    success_url=reverse_lazy('ecomapp:home')
     
    def dispatch(self, request, *args, **kwargs):
         if request.user.is_authenticated and request.user.customer:
             pass
         else:
            return  redirect('/login/?next=/checkout/')
         return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        cart_id=self.request.session.get('cart_id')
        if cart_id:
             cart_obj=Cart.objects.get(id=cart_id)

        else:
            cart_obj=None

        context['cart']=cart_obj         

        return context
    
    def form_valid(self, form):
        cart_id=self.request.session.get('cart_id')
        if cart_id:
            cart_obj=Cart.objects.get(id=cart_id)
            form.instance.cart=cart_obj
            form.instance.subtotal=cart_obj.total
            form.instance.discount=0
            form.instance.total=cart_obj.total
            form.instance.order_status='ORDER_RECEIVED'
            del self.request.session['cart_id']
        return super().form_valid(form)
    

class CustomerRegisterView(CreateView):
    template_name='customerregister.html'
    form_class=CustomerRegisterForm
    success_url= reverse_lazy('ecomapp:home') 

    def form_valid(self, form):
        username=form.cleaned_data.get('username')
        email=form.cleaned_data.get('email')
        password=form.cleaned_data.get('password')
        user=User.objects.create_user(username,email,password)
        form.instance.user=user
        return super().form_valid(form)  
    

class LogoutView(View):
    def get(self,requst):
        logout(requst)
        return redirect('ecomapp:home')
    

class LoginView(FormView):
    template_name='login.html'
    form_class=LoginForm
    success_url=reverse_lazy('ecomapp:home')   
    def form_valid(self, form):
        uname=form.cleaned_data.get('username')
        pword=form.cleaned_data.get('password')
        usr=authenticate(username=uname,password=pword)
        if usr is not None and usr.customer:
            login(self.request,usr)

        else:
            return render(self.request,self.template_name,{'form':self.form_class,'error':'invalid credentials'})    
        return super().form_valid(form) 
    
    def get_success_url(self):
        if 'next' in self.request.GET:
            next_url=self.request.GET.get('next')
            return next_url
        
        else:
            return self.success_url
        return super().get_success_url()

    
   
    

class Aboutview(EcomMixin,TemplateView):
    template_name='about.html'


class Contactview(EcomMixin,TemplateView):
    template_name='contact.html'  

class CustomerProfileView(TemplateView):
    template_name='customerprofile.html'

    def dispatch(self, request, *args, **kwargs):
         if request.user.is_authenticated and request.user.customer:
             pass
         else:
            return  redirect('/login/?next=/profile/')
         return super().dispatch(request, *args, **kwargs)
    

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        customer=self.request.user.customer
        context['customer']=customer
        order=Order.objects.filter(cart__customer=customer)
        context['orders']=order
        return context
    
class CustomerOrderDetailView(DetailView):
    template_name='orderdetail.html'
    model=Order
    context_object_name='order_obj' 

    def dispatch(self, request, *args, **kwargs):
         if request.user.is_authenticated and request.user.customer:
             pass
         else:
            return  redirect('/login/?next=/profile/')
         return super().dispatch(request, *args, **kwargs)  
    

class AdminMixinView(object):
     def dispatch(self, request, *args, **kwargs):
         if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
             pass
         else:
            return  redirect('/admin-login/')
         return super().dispatch(request, *args, **kwargs)



class AdminLoginView(AdminMixinView,FormView):
    template_name='adminpages/adminlogin.html'
    form_class=LoginForm
    success_url=  reverse_lazy('ecomapp:adminhome') 

    def form_valid(self, form):
        uname=form.cleaned_data.get('username')
        pword=form.cleaned_data.get('password')
        usr=authenticate(username=uname,password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request,usr)

        else:
            return render(self.request,self.template_name,{'form':self.form_class,'error':'invalid credentials'})  

        return super().form_valid(form)  

class AdminHomeView(AdminMixinView,TemplateView):
    template_name='adminpages/adminhome.html'   
    
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['orders']=Order.objects.filter(order_status='ORDER_RECEIVED').order_by('-id')
        return context
    
class AdminOrderDetailView(AdminMixinView,DetailView):
    template_name='adminpages/adminorderdetail.html'
    model=Order
    context_object_name='order_obj'

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['allstatus']=ORDER_STATUS
        return context


class AdminAllOrdersView(AdminMixinView,ListView): 
    template_name='adminpages/adminorderlist.html'
    queryset=Order.objects.all().order_by('-id')   
    context_object_name='orders'

class AdminOrderStatusView(AdminMixinView,View):
    def post(self, request, *args, **kwargs):
        order_id=self.kwargs['pk']
        order_obj=Order.objects.get(id=order_id)
        new_status=request.POST.get('status')
        order_obj.order_status=new_status
        order_obj.save()

        return redirect(reverse_lazy('ecomapp:adminorderdetail', kwargs={'pk':order_id}))
    
class SearchView(TemplateView):
    template_name='search.html'  

    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs) 
        keywd=self.request.GET.get('keyword')
        results=Product.objects.filter(title__contains=keywd)
        context['results']=results
        return context






    
        



    