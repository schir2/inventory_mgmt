from django.contrib.auth import get_user_model
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from simple_history.models import HistoricalRecords
from inventory.exceptions import ProductStatusError, StockLogicError, ProductConditionError, ProductOrderAssignmentError


class Category(MPTTModel):
    name = models.CharField(max_length=64)
    slug = models.SlugField()
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name', ]

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return f'{self.name}'


class Email(models.Model):
    #  TODO  Write Description
    email = models.EmailField(blank=True)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = _('Email')
        verbose_name_plural = _('Emails')


class PhoneNumber(models.Model):
    #  TODO  Write Description
    phone_number = PhoneNumberField(default='', blank=True)

    def __str__(self):
        return f'{self.phone_number}'

    class Meta:
        verbose_name = _('Phone Number')
        verbose_name_plural = _('Phone Numbers')


class Contact(models.Model):
    #  TODO  Write Description
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    emails = models.ManyToManyField('Email', through='ContactEmail', related_name='emails')
    phone_numbers = models.ManyToManyField('PhoneNumber', through='ContactPhoneNumber', related_name='phone_numbers')
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = _('Contact')
        verbose_name_plural = _('Contacts')
        ordering = ('first_name', 'last_name',)


class ContactEmail(models.Model):
    #  TODO  Write Description
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    email = models.ForeignKey('Email', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.email}'

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class ContactPhoneNumber(models.Model):
    #  TODO  Write Description
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)
    phone_number = models.ForeignKey('PhoneNumber', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.contact} | {self.phone_number}'

    class Meta:
        verbose_name = _('Contact Phone Number')
        verbose_name_plural = _('Contact Phone Numbers')


class CustomerContact(models.Model):
    #  TODO  Write Description
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    contact = models.ForeignKey('Contact', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.customer} | {self.contact}'

    class Meta:
        verbose_name = _('Customer Contact')
        verbose_name_plural = _('Customer Contacts')


class Customer(MPTTModel):
    #  TODO  Write Description
    #  TODO  Fix bug with history model
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    company_name = models.CharField(max_length=150, blank=True, default='')
    contact = models.ManyToManyField('Contact', through='CustomerContact', related_name='contact')
    location = models.ManyToManyField('Location', through='CustomerLocation', related_name='location')
    parent = TreeForeignKey('self', on_delete=models.PROTECT, blank=True, null=True)

    def get_absolute_url(self):
        return reverse_lazy('inventory:customer_detail', kwargs={'pk': self.pk})

    @property
    def name(self) -> str:
        return f'{self.company_name}' if self.company_name else f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class MPTTMeta:
        order_insertion_by = ['company_name', 'first_name', 'last_name', ]

    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ('company_name', 'first_name', 'last_name',)


class GenericProduct(models.Model):
    """A generic product container that relates to different versions of the same product.
    For example: a product having different brands or different sizes or colors
    """

    class GenericProductStatus(models.TextChoices):
        """Product status choices
        Stored: Product stored in Stock
        Deployed: Product deployed at customer location
        Decommissioned: Product no longer in use and not in inventory
        Inactive: The product is no longer active but is still stored in the inventory
        Recall: The product is inactive and should no longer be used.
        Picked Up: Product is currently with the employee. Not at any customer location or inventory.
        """
        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACTIVE', _('Inactive')
        RECALL = 'RECALL', _('Recall')

    category = TreeForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=150, unique=True)
    status = models.CharField(max_length=16, choices=GenericProductStatus.choices, default=GenericProductStatus.ACTIVE)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Generic Product')
        verbose_name_plural = _('Generic Products')


class Brand(models.Model):
    #  TODO  Write Description
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Brand')
        verbose_name_plural = _('Brands')


class ProductType(models.Model):
    #  TODO  Write Description
    name = models.CharField(max_length=64)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Product Type')
        verbose_name_plural = _('Product Types')


class Product(models.Model):
    """An inventory item that can be inventoried"""

    class Condition(models.TextChoices):
        """Current condition of an inventory item. New: Brand new inventory item that has not been used. When the
        inventory item is picked up it is automatically changed to working. Working: Product is in good working
        condition Damaged: Product is damaged and needs repair Irreparable: Product is damaged beyond repair. This
        inventory item should be decommissioned
        """
        NEW = 'NEW', _('New')
        WORKING = 'WORKING', _('Working')
        DAMAGED = 'DAMAGED', _('Damaged')
        IRREPARABLE = 'IRREPARABLE', _('Irreparable')


    class ProductStatus(models.TextChoices):
        """Product status choices
        Stored: Product stored in Stock
        Deployed: Product deployed at customer location
        Decommissioned: Product no longer in use and not in inventory
        Inactive: The product is no longer active but is still stored in the inventory
        Recall: The product is inactive and should no longer be used.
        Picked Up: Product is currently with the employee. Not at any customer location or inventory.
        """
        STORED = 'STORED', _('Stored')
        DEPLOYED = 'DEPLOYED', _('Deployed')
        DECOMMISSIONED = 'DECOMMISSIONED', _('Decommissioned')
        INACTIVE = 'INACTIVE', _('Inactive')
        RECALL = 'RECALL', _('Recall')
        PICKED_UP = 'PICKED_UP', _('Picked Up')

    name = models.CharField(max_length=150)
    generic_name = models.ForeignKey('GenericProduct', on_delete=models.PROTECT)
    brand = models.ForeignKey('Brand', on_delete=models.CASCADE)
    product_type = models.ForeignKey(ProductType, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=ProductStatus.choices, default=ProductStatus.STORED)
    condition = models.CharField(max_length=16, choices=Condition.choices, default=Condition.NEW)
    stock = models.ForeignKey('Stock', on_delete=models.SET_NULL, blank=True, null=True)
    employee = models.ForeignKey(get_user_model(), related_name='product_employee', on_delete=models.SET_NULL,
                                 null=True, blank=True)
    order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    def get_absolute_url(self):
        return reverse_lazy('inventory:product_detail', kwargs={'pk': self.pk})

    def store(self, stock_id: int = None) -> 'Product':
        """Stores the inventory item at a inventory location. By default the inventory item is returned to it's
        original location. If a inventory_id is supplied the inventory item is moved to a new inventory location with
        the given inventory_id """
        if self.status == ProductStatus.DECOMMISSIONED:
            raise ProductStatusError('decommissioned inventory item cannot be stored')
        if stock_id is None and self.stock_id is None:
            raise StockLogicError(
                _('the current inventory item does not have a inventory associated with it. A inventory_id must be '
                  'passed'))
        if self.status == ProductStatus.STORED and self.stock_id and stock_id and int(self.stock_id) == int(
                stock_id):
            raise StockLogicError(_('cannot store stock item in a location it is already stored in'))
        if stock_id is not None:
            self.stock_id = stock_id
        self.employee = None
        self.status = ProductStatus.STORED
        return self.save()

    def pickup(self, employee_id: int) -> 'Product':
        """Product is picked up from a customer location or a inventory location. An employee is assigned to the
        inventory item. """
        if self.status == ProductStatus.DECOMMISSIONED:
            raise ProductStatusError(_('decommissioned inventory item cannot be picked up'))
        if self.condition == self.Condition.NEW:
            self.condition = self.Condition.WORKING
        if self.employee_id == employee_id:
            raise StockLogicError(_('the same user cannot pick up an inventory item they are already holding'))
        self.employee_id = employee_id
        self.status = ProductStatus.PICKED_UP
        return self.save()

    def deploy(self, location_id: int, order_id: int = None) -> 'Product':
        if not order_id and not self.order:
            raise ProductOrderAssignmentError(_('A order must be assigned to deploy the product'))
        """Deploys the inventory item at a customer location"""
        if self.status == ProductStatus.DECOMMISSIONED:
            raise ProductStatusError(_('decommissioned inventory item cannot be deployed'))
        if self.status != ProductStatus.PICKED_UP:
            raise ProductStatusError(_('item must be picked up before it can be deployed'))
        if self.condition in self.Condition.DAMAGED or self.Condition.IRREPARABLE:
            raise ProductConditionError(_('broken or irreparable item cannot be deployed'))
        self.status = ProductStatus.DEPLOYED
        return self.save()

    def decommission(self) -> 'Product':
        """Decommissions the item and removes all employee, inventory, and location associations"""
        notification_message: str = ''  # TODO  Add notification message for decommissioning an item.
        self.employee = None
        self.stock = None
        self.status = ProductStatus.DECOMMISSIONED
        return self.save()


class Location(models.Model):
    name = models.CharField(max_length=150, blank=True)
    street_number = models.CharField(max_length=20, blank=True)
    route = models.CharField(max_length=100, blank=True)
    raw = models.CharField(max_length=200)
    formatted = models.CharField(max_length=200, blank=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    def get_absolute_url(self):
        return reverse_lazy('inventory:location_detail', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        self.name = self.name or self.formatted or self.raw
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ('name',)


class CustomerLocation(models.Model):
    #  TODO  Write Description
    location = models.ForeignKey('Location', on_delete=models.CASCADE)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.location} | {self.customer}'

    class Meta:
        verbose_name = _('Customer Location')
        verbose_name_plural = _('Customer Locations')


class Stock(models.Model):
    """A holder for all inventory items"""

    class StockStatus(models.TextChoices):
        """Choices for setting the status of a stock location
        Active: Available for picking up and dropping off items
        Inactive: Not in use. Products cannot be picked up or dropped off from this location
        Full: The inventory location is currently full. No items can be dropped off.
        """

        ACTIVE = 'ACTIVE', _('Active')
        INACTIVE = 'INACTIVE', _('Inactive')
        FULL = 'FULL', _('Full')

    name = models.CharField(max_length=150, blank=True)
    status = models.CharField(max_length=16, choices=StockStatus.choices, default=StockStatus.ACTIVE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    history = HistoricalRecords()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Stock')
        verbose_name_plural = _('Stocks')

    def get_absolute_url(self):
        return reverse_lazy('stock:stock_detail', kwargs={'pk': self.pk})


class Notification(models.Model):
    """TODO  Implement this class"""
    pass


class NotificationPreference(models.Model):
    """TODO  Implement this class"""
    pass


class Order(models.Model):
    """Model for scheduling orders to allow easier assignment of inventory, services and products"""

    class OrderStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', _('Active')
        CANCELED = 'CANCELED', _('Canceled')
        COMPLETED = 'COMPLETED', _('Completed')

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    status = models.CharField(max_length=16, choices=OrderStatus.choices, default=OrderStatus.ACTIVE)
    employee = models.ManyToManyField(get_user_model(), related_name='order_employees')
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateTimeField()
    history = HistoricalRecords()

    def save(self, **kwargs):
        # TODO Implement a method that only allows updates if the order is in active status.
        return super().save(**kwargs)

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    def __str__(self):
        return f'Order {self.id} for {self.customer} @ {self.date}'
