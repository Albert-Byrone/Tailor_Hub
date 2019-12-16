from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from django.contrib.auth import login, authenticate
from django.utils import timezone
from django.views.generic import ListView,DetailView,View
from .forms import UpdateUserForm,SignUpForm,PostForm,UpdateUserProfileForm,CommentForm,CheckoutForm,CouponForm,RefundForm
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin   
import stripe
import random
import string
stripe.api_key = settings.STRIPE_SECRET_KEY


# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=30))

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            messages.info(request,"Account successfully created")
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'registration/registration_form.html', {'form': form})

def home(request):
    items = Item.objects.all()
    users = User.objects.exclude(id=request.user.id)
    form = PostForm(request.POST,request.FILES)
    if request.method == "POST":
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.profile
            post.save()
            return HttpResponseRedirect(request.path_info)
        else:
            form = PostForm()
      
    context = {
        'items': items,
        'form': form,
        'users': users,
        
       
    }
    return render(request,'home-page.html',context)


class CheckoutView(View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user,is_ordered=False)
            form= CheckoutForm()
            Couponform=CouponForm()
            context = {
                'form': form,
                'Couponform':'Couponform',
                'order':order
            }
            return render(self.request,'checkout.html',locals())
        except ObjectDoesNotExist:
            messages.info(self.request,"You do not have an active order ")
            return redirect("tailor:checkout")
        
        
