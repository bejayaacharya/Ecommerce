
from django import forms
from .models import *


class CheckOutForm(forms.ModelForm):
    class Meta:
        model=Order
        fields =['order_by','shipping_address','mobile','email']


class CustomerRegisterForm(forms.ModelForm):
    username=forms.CharField(widget=forms.TextInput())
    password=forms.CharField(widget=forms.PasswordInput())
    email=forms.EmailField(widget=forms.EmailInput())
    class Meta:
        model=Customer
        fields=['username','password','email','full_name','address']   

    def clean_username(self):
        uname=self.cleaned_data.get('username')
        if User.objects.filter(username=uname).exists():
            raise forms.ValidationError('username already taken')   
        return uname   
    

class LoginForm(forms.Form):
    username=forms.CharField(widget=forms.TextInput())
    password=forms.CharField(widget=forms.PasswordInput())    
