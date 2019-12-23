from django.shortcuts import render,get_object_or_404,redirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .forms import * 
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
                'order':order,
                # 'DISPLAY_COUPON_FORM':True
            }
            
            return render(self.request,'checkout.html',locals())
        except ObjectDoesNotExist:
            messages.info(self.request,"You do not have an active order ")
            return redirect("tailor:checkout")
        
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
                    messages.warning(self.request,"Invalid payment option selected ")
                    return redirect('tailor:checkout')   
        except ObjectDoesNotExist:
            messages.warning(self.request,"You do not have an active order")
            return redirect("tailor:order-summary")


class PaymentView(View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,is_ordered=False)
        if order.billing_address:
            context = {
                'order':order,
                # 'DISPLAY_COUPON_FORM':False
            }
            return render(self.request,"payment.html",context)
        else:
            messages.warning(self.request,"You have not added any address")
            return redirect("tailor:checkout")

    def post(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user,is_ordered=False)
        form = PaymentForm(self.request.POST)
        userprofile = Profile.objects.get(user=self.request.user)
        if form.is_valid():
            token = form.cleaned_data.get('stripeToken')
            print(token,"aaaaaaaaaaaaaaa")
            save = form.cleaned_data.get('save')
            use_default = form.cleaned_data.get('user_default')

            if save:
                if userprofile.stripe_customer.id !='' and userprofile.stripe_customer_id is not None:
                    customer = stripe.Customer.retrieve(
                        userprofile.stripe_customer_id
                    )
                    customer.source.create(source=token)
                else:
                    customer = stripe.Customer.create(
                        email=self.request.user
                    )
                    customer.source.create(source=token)
                    userprofile.stripe_customer_id = customer['id']
                    userprofile.one_click_purchasing = True
                    userprofile.save()
            amount = int(order.get_total() * 100)
            try:
                if use_default or save:
                    #charge the customer
                    charge = stripe.Charge.create(
                        amount = amount,
                        currency = "usd",
                        source = token 
                    )
                else:
                    #charge off the token
                    charge = stripe.Charge.create(
                        amount= amount,
                        currency = "usd",
                        source= token
                    )
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
                messages.warning(self.request,f"{ err.get('message')}")
                return redirect("/")
            except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
                messages.warning(self.request,"Rate linit error ")
                return redirect("/")
            except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
                messages.warning(self.request,f"error occurred {e}")
                return redirect("/")
            except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
                messages.warning(self.request,"Not authenticated ")
                return redirect("/")
            except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
                messages.warning(self.request,"Network error")
                return redirect("/")

            except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
                messages.warning(self.request,"Something went wrong..You were not charged.Try again")
                return redirect("/")

            except Exception as e:
            # Something else happened, completely unrelated to Stripe
                messages.warning(self.request,"Its something wrong,We are working on it")
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
            messages.warning(self.request,"You do not have an active order")
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


# @login_required(login_url='/accounts/login')
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


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'


# login_required(login_url='/accounts/login')
def add_to_cart(request, pk):
    item = get_object_or_404(Item,pk=pk)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        is_ordered=False
        )
    order_qs = Order.objects.filter(user= request.user,is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the item exist in thecart
        if order.items.filter(item__id=item.id).exists():
            order_item.quantity+=1
            order_item.save()
            messages.info(request,"Quantity  successfully updated" )
            return redirect("tailor:order-summary")
        else:
            messages.info(request,"Addded successfully")
            order.items.add(order_item)
            return redirect("tailor:order-summary")
    else:
        ordered_date = timezone.now()
        order= Order.objects.create(user=request.user,ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request,"Addded successfully" )
        return redirect("tailor:order-summary")

# @login_required(login_url='/accounts/login')
def remove_from_cart(request,pk):
    item = get_object_or_404(Item,pk=pk)
    order_qs = Order.objects.filter(user= request.user,is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]\
        # check if the item exist in thecart
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request,"Removed successfully" )
            return redirect("tailor:order-summary")
        else:
            messages.info(request,"No order with that order item")
            return redirect("tailor:product",pk=pk)     
    else:
        messages.info(request,"You do not have an active order ")
        return redirect("tailor:product",pk=pk)



# @login_required(login_url='/accounts/login')
def remove_single_item_from_cart(request,pk):
    item = get_object_or_404(Item,pk=pk)
    order_qs = Order.objects.filter(user= request.user,is_ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the item exist in thecart
        if order.items.filter(item__id=item.id).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                is_ordered=False
            )[0]
            if order_item.quantity >1:
                order_item.quantity-=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request,"Item quantity updated " )
            return redirect("tailor:order-summary")
        else:
            messages.info(request,"No order with that order item")
            return redirect("tailor:product")     
    else:
        messages.info(request,"You do not have an active order ")
        return redirect("tailor:product")

def get_coupon(request, code ):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.info(request,"Invalid Coupon ")
        return redirect("tailor:checkout")

class AddCouponView(View):
    def post(self,*args,**kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user,is_ordered=False)
                order.coupon = get_coupon(self.request,code)
                order.save()
                messages.success(self.request,"Coupon successfully Applied")
                return redirect("tailor:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request,"You do not have an active order ")
                return redirect("tailor:checkout")
             

class RequestRefundView(View):
    def get(self,*args,**kwargs):
        form = RefundForm()
        context = {
            'form':form
        }
        return render(self.request,"request_refund.html",locals())

        def post(self, *args, **kwargs):
            form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("core:request-refund")