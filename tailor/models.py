from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse
from pyuploadcare.dj.models import ImageField
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime as datetime
from django_countries.fields import CountryField
from django.db.models import Q



CATEGORY_CHOICES=(
    ('SU','Suits'),
    ('TR','Trousers'),
    ('CO','Coats'),
    ('DR','Dresses')
)
LABEL_CHOICES=(
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)
class Profile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name='profile')
    prof_pic = models.ImageField(upload_to='images/',default='./img/avator.png')
    bio = models.TextField(max_length=50,default='this is my bio')
    name = models.CharField(blank=True,max_length=120)
    contact =models.PositiveIntegerField(null=True,blank=True)
    email = models.EmailField()
    location = models.CharField(max_length=60, blank=True)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)


    def __str__(self):
        return f'{self.user.username} Profile'

    @receiver(post_save,sender=User)
    def create_user_profile(sender,instance,created,**kwargs):
        if created:
            userprofile = Profile.objects.create(user=instance)

    @receiver(post_save,sender=User)
    def save_user_profile(sender,instance,created,**kwargs):
            instance.profile.save()
    
    def save_profile(self):
        return self.save()

    def delete_profile(self):
        return self.delete()

    @classmethod
    def search_profile(cls,name):
        return cls.objects.filter(user__username__icontains=name).all()

class Item(models.Model):
    title = models.CharField(max_length=200)
    price = models.FloatField()
    discount_price = models.FloatField(null=True,blank=True,default="0")
    category = models.CharField(choices=CATEGORY_CHOICES,max_length=2,default="SU")
    label = models.CharField(choices=LABEL_CHOICES,max_length=1,default="P")
    photo = models.ImageField(null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts')
    created = models.DateTimeField(auto_now_add=True, null=True)

    def get_all_comments(self):
        return self.comments.all()

    @classmethod
    def search_term(cls,searchterm):
        search = Item.objects.filter(Q(title__icontains=searchterm)|Q(description__icontains=searchterm)|Q(category__icontains=searchterm))
        return search


    def __str__(self):
        return f"{self.title}"


class Comment(models.Model):
    comment = models.TextField()
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    created = models.DateTimeField(auto_now_add=True, null=True)

class OrderItem(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    item = models.ForeignKey(Item,on_delete=models.CASCADE)
    is_ordered = models.BooleanField(default=False)
    quantity = models.IntegerField(default=1)


    def __str__(self):
        return f"{self.quantity} of {self.item.title}"

    def get_total_price(self):
        return self.quantity * self.item.price

    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price

    def get_amount_saved(self):
        return self.get_total_price() - self.get_total_discount_price()

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return  self.get_total_price()


class Order(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=30)
    is_ordered = models.BooleanField(default=False)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    billing_address = models.ForeignKey('BillingAddress',on_delete=models.SET_NULL,null=True,blank=True)
    payment = models.ForeignKey('Payment',on_delete=models.SET_NULL,null=True,blank=True)
    coupon = models.ForeignKey('Coupon',on_delete=models.SET_NULL,null=True,blank=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_approved = models.BooleanField(default=False)

    def __str__(self):
         return f"{ self.user.username }"

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total

class BillingAddress(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=50)
    apartment_address=models.CharField(max_length=50)
    country = CountryField(multiple=False,default="Kenya")
    zipcode = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.user.username }"

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User,on_delete=models.SET_NULL,blank=True,null=True)
    amount= models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{ self.user.username }"


class Coupon(models.Model):
    code  =  models.CharField(max_length=15)
    amount = models.FloatField(default=50)

    def __str__(self):
        return f"{self.code }"

class Refund(models.Model):
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    

    def __str__(self):
        return f"{ self.pk }"