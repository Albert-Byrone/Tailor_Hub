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

