from django.contrib.admin import register, ModelAdmin, TabularInline
from simple_history.admin import SimpleHistoryAdmin
from mptt.admin import MPTTModelAdmin
from inventory.models.contact import Contact, ContactPhoneNumber, ContactEmail
from inventory.models.order import Order, OrderGenericProduct
from inventory.models.stock import Stock
from inventory.models.location import Location
from inventory.models.equipment import Equipment
from inventory.models.product import Product, ProductType, Brand
from inventory.models.generic_product import GenericProduct, Category
from inventory.models.customer import Customer, CustomerLocation


class GenericProductInline(TabularInline):
    model = OrderGenericProduct


@register(CustomerLocation)
class CustomerLocationAdmin(SimpleHistoryAdmin):
    list_display = ('customer', 'location')


@register(ContactEmail)
class ContactEmailAdmin(SimpleHistoryAdmin):
    list_display = ('contact', 'email',)


@register(ContactPhoneNumber)
class ContactPhoneNumberAdmin(SimpleHistoryAdmin):
    list_display = ('contact', 'phone_number',)


@register(GenericProduct)
class GenericProductAdmin(SimpleHistoryAdmin):
    list_display = ('name',)
    list_filter = ('name', 'category',)
    search_fields = ('category__name',)


@register(Customer)
class CustomerAdmin(SimpleHistoryAdmin):
    list_display = ('first_name', 'last_name', 'company_name', 'parent')


@register(Contact)
class ContactAdmin(SimpleHistoryAdmin):
    list_display = ('first_name', 'last_name',)


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = ('name', 'brand', 'product_type', 'generic_product', 'status', 'count',)
    history_list_display = list_display


@register(Equipment)
class EquipmentAdmin(SimpleHistoryAdmin):
    list_display = ('id', 'name', 'status', 'stock', 'employee', 'order',)
    readonly_fields = ('counter', 'name',)


@register(Stock)
class StockAdmin(SimpleHistoryAdmin):
    list_display = ('name', 'status', 'location',)


@register(Category)
class CategoryAdmin(MPTTModelAdmin):
    ...


@register(ProductType)
class ProductTypeAdmin(SimpleHistoryAdmin):
    list_display = ('name',)


@register(Brand)
class BrandAdmin(SimpleHistoryAdmin):
    list_display = ('name',)


@register(OrderGenericProduct)
class OrderGenericProductAdmin(ModelAdmin):
    ...


@register(Location)
class LocationAdmin(SimpleHistoryAdmin):
    ...


@register(Order)
class OrderAdmin(SimpleHistoryAdmin):
    list_display = ['id', 'customer', 'location', 'date', 'employee_names']
    inlines = (GenericProductInline,)

    def employee_names(self, obj: Order):
        return ', '.join(employee.username for employee in obj.employees.all())
