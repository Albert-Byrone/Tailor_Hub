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
    prof_pic = models.ImageField(upload_to='images/',default='text.png')
    bio = models.TextField(max_length=50,default='this is my bio')
    name = models.CharField(blank=True,max_length=120)
    contact =models.PositiveIntegerField(null=True,blank=True)
    email = models.EmailField()
    location = models.CharField(max_length=60, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'

    @receiver(post_save,sender=User)
    def create_user_profile(sender,instance,created,**kwargs):
        if created:
            Profile.objects.create(user=instance)

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

