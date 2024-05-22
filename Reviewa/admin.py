# Register your models here.
from django.contrib import admin
from .models import User, Business, Product, Feedback


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'phone')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering = ('email',)


admin.site.register(User, UserAdmin)


class BusinessAdmin(admin.ModelAdmin):
    list_display = ('store_name',)
    search_fields = ('store_name',)
    ordering = ('store_name',)


admin.site.register(Business, BusinessAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name',)
    search_fields = ('product_name',)
    list_filter = ('business',)
    ordering = ('product_name',)


admin.site.register(Product, ProductAdmin)



class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rate', 'comment', 'time_date')
    search_fields = ('user__email', 'product__product_name', 'comment', 'time_date')
    list_filter = ('rate', 'time_date', 'user', 'product')
    ordering = ('-id',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('user', 'product', 'rate', 'comment')
        return self.readonly_fields


admin.site.register(Feedback, FeedbackAdmin)
