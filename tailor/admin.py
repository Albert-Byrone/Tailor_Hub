from django.contrib import admin
from .models import Item,OrderItem,Order,Profile,Comment,BillingAddress,Coupon


def accept_refund(ModelAdmin,request,queryset):
    queryset.update(refund_requested=False,refund_approved=True)
accept_refund.short_description = 'Approve refund'

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'is_ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_approved',
        'billing_address',
        'payment',
        'coupon'
        ]
    list_display_link = [
        'user',
        'billing_address',
        'payment',
        'coupon'
    ]
    list_filter = [
        'is_ordered',
        'being_delivered',
        'received',
        'refund_requested',
        'refund_approved'
    ]
    search_fields =[
        'user__username',
        'ref_code'
    ]
    actions =[accept_refund]


admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order,OrderAdmin)
admin.site.register(Profile)
admin.site.register(Comment)
admin.site.register(BillingAddress)
admin.site.register(Coupon)