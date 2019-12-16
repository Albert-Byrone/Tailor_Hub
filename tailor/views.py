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
        
        
    @login_required(login_url='/accounts/login')
    def post(self,*args,**kwargs):
        form= CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)   
            if form.is_valid():
                street_address= form.cleaned_data.get('street_address')
                apartment_address= form.cleaned_data.get('apartment_address')
                country= form.cleaned_data.get('country')
                zipcode= form.cleaned_data.get('zipcode')
                same_billing_address= form.cleaned_data.get('same_billing_address')
                save_info= form.cleaned_data.get('save_info')
                payment_option= form.cleaned_data.get('payment_option')
                billing_address  = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zipcode = zipcode
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()

                if payment_option == 'S':
                    return redirect('tailor:payment',payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('tailor:payment',payment_option='paypal')
                else:
                    messages.error(self.request,"Invalid payment option selected ")
                    return redirect('tailor:checkout')   
        except ObjectDoesNotExist:
            messages.error(self.request,"You do not have an active order")
            return redirect("tailor:order-summary")


class PaymentView(View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,is_ordered=False)
        context = {
            'order':order
        }
        return render(self.request,"payment.html",context)

    def post(self,*args,**kwargs):

        order = Order.objects.get(user=self.request.user,is_ordered=False)
        token = self.request.POST.get('stripeToken')
        print(token)
        amount = order.get_total()
        amountt =  order.get_total()
        print(amount,"amount")
        print(amountt,"amountttt")
        try:

            charge = stripe.Charge.create(
                amount=amount,
                currency="usd",
                source=token,
                
                )
            #create payment
            payment = Payment()
            payment.stripe_charge_id = charge.id
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            #assign payment to the order

            order_items = order.items.all()
            order_items.update(is_ordered=True)
            for item in order_items:
                item.save()

            order.is_ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()  
            messages.success(self.request,"You order was succesfull")
            return redirect("/")
        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error',{})
            messages.error(self.request,f"{ err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
        # Too many requests made to the API too quickly
            messages.error(self.request,"Rate linit error ")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
            messages.error(self.request,f"error occurred {e}")
            return redirect("/")

        except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
            messages.error(self.request,"Not authenticated ")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
            messages.error(self.request,"Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
            messages.error(self.request,"Something went wrong..You were not charged.Try again")
            return redirect("/")

        except Exception as e:
        # Something else happened, completely unrelated to Stripe
            messages.error(self.request,"Its something wrong,We are working on it")
            return redirect("/")
      
       

class OrderSummaryView(LoginRequiredMixin, View):
    def get(self,*args,**kwargs):

        try:
            order = Order.objects.get(user=self.request.user, is_ordered=False)
            context = {
                'order':order
            }
            return render(self.request,'order_summary.html',locals())
        except ObjectDoesNotExist:
            messages.error(self.request,"You do not have an active order")
            return redirect("/")

@login_required(login_url='/accounts/login')
def profile(request,**kwargs):
    # profile = User.objects.filter(username=username)
    usr_profile = get_object_or_404(Profile,pk=kwargs["id"])

    print(usr_profile)
    images = Item.objects.filter(user=kwargs['id'])
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        prof_form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and prof_form.is_valid():
            user_form.save()
            prof_form.save()
            return HttpResponseRedirect(request.path_info)
    else:
        user_form = UpdateUserForm(instance=request.user)
        prof_form = UpdateUserProfileForm(instance=request.user.profile)
    params = {
        'user_form': user_form,
        'prof_form': prof_form,
        'images': images,  
        'profile':profile, 
    }
    return render(request, 'profile/profile.html', locals())


@login_required(login_url='/accounts/login')
def user_profile(request, username):
    user_prof = get_object_or_404(User, username=username)
    if request.user == user_prof:
        return redirect('profile', username=request.user.username)
    user_posts = user_prof.profile.posts.all()
    users = User.objects.get(username=username)
    params = {
        'user_prof': user_prof,
        'user_posts': user_posts,
    }
    return render(request, 'profile/user_profile.html', params)

# class HomeView(ListView):
#     # model = Item
#     # template_name = 'home-page.html'

