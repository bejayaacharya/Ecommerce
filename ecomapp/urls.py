
from django.urls import path
from .views import *

app_name='ecomapp'

urlpatterns=[
    path('', Homeview.as_view(), name='home'),
    path('about/', Aboutview.as_view(),name='about'),
    path('contact/',Contactview.as_view(),name='contact'),
    path('allproduct/',AllProductView.as_view(),name='allproduct'),
    path('product/<slug:slug>',ProductDetailView.as_view(),name='productdetail'),
    path('add-to-cart/<int:pro_id>/',AddToCartView.as_view(), name='addtocart'),
    path('my-cart/',MyCartView.as_view(),name='mycart'),
]

