
from django.conf.urls import url,include
from django.conf.urls.static import static
from django.conf import settings
from .views import (
    # HomeView,
    ItemDetailView,
    add_to_cart,
    remove_from_cart,
    OrderSummaryView,
    remove_single_item_from_cart,
    CheckoutView,
    PaymentView,
    RequestRefundView,
    AddCouponView,
)
from . import views
    
app_name = 'tailor'

urlpatterns = [
    url(r'signup/$', views.signup, name='signup'),
    url(r'^$',views.home,name="home"),
    url(r'^user_profile/(?P<username>\w+)', views.user_profile, name='user_profile'),
    url(r'^profile/(?P<id>\d+)', views.profile, name='profile'),
    url(r'^product/(?P<pk>\d+)/$', ItemDetailView.as_view(), name='product'),
    url(r'^order-summary/$',OrderSummaryView.as_view(), name='order-summary'),
    url(r'checkout/$', CheckoutView.as_view(), name='checkout'),
    url(r'^add-to-cart/(?P<pk>\d+)/$',add_to_cart, name='add-to-cart'),
    url(r'^add-coupon/$',AddCouponView.as_view(), name='add-coupon'),
    url(r'^remove-from-cart/(?P<pk>\d+)/$',remove_from_cart, name='remove-from-cart'),
    url(r'^remove_single_item_from_cart/(?P<pk>\d+)/$',remove_single_item_from_cart, name='remove_single_item_from_cart'),
    url(r'payment/(?P<payment_option>)', PaymentView.as_view(), name='payment'),
    url(r'request-refund/$',RequestRefundView.as_view(),name='request-refund'),
     
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

