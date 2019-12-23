from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from pyuploadcare.dj.forms import ImageField
from django_countries.fields import CountryField
from django_countries.fields import CountryField
from .models import Item,OrderItem,Order,Profile,Comment
from django_countries.widgets import CountrySelectWidget

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class UpdateUserForm(forms.ModelForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email')
class UpdateUserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['name', 'location','contact', 'prof_pic', 'bio','email',]

class PostForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('title', 'price','discount_price','category','photo','description','label')

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['comment'].widget = forms.TextInput()
        self.fields['comment'].widget.attrs['placeholder'] = 'Add a comment...'

    class Meta:
        model = Comment
        fields = ('comment',)
PAYMENT_OPTIONS=(
    ("S","Stripe"),
    ("P","Paypal")
)
class CheckoutForm(forms.Form):
    shipping_address =  forms.CharField(required=False)
    shipping_address2 =  forms.CharField(required=False)
    shipping_country = CountryField(blank_label='Select Country').formfield(widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100'
    }))
    shipping_zipcode =  forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_billing_address = forms.BooleanField(required=False)
    save_info = forms.BooleanField(required=False)
    payment_option=  forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_OPTIONS)

class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Promo code',
        'aria-label':'Recipient\'s username',
        'aria-describedby':'basic-addon2'
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message =  forms.CharField(widget=forms.Textarea(attrs={
        'rows':5,
    }))
    email =  forms.EmailField()

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)