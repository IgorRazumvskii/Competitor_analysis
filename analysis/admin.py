from django.contrib import admin
from .models import Store, Product


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'url')
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('vendor_code', 'name', 'price', 'get_store_name', 'date')
    search_fields = ('vendor_code', 'name')
    list_filter = ('store', 'date')
    filter_horizontal = ('user',)

    def get_store_name(self, obj):
        return obj.store.name
    get_store_name.short_description = 'Store Name'
    get_store_name.admin_order_field = 'store__name'

