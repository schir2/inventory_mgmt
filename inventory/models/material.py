from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel

from common.models.field import Field
from inventory.models.brand import Brand
from common.models.target import Target
from common.models.unit import Unit
from inventory.models.vendor import Vendor


class Material(models.Model):
    """
        Model for a Material
        A material is a physical item that can be used in the provision of a service.
        Each material has a name and a unique identifier, and can be associated with multiple material classes.
        The priority of the material within a material class determines its suggested order of use.
    """

    # TODO  Add Min Stock / Max Stock

    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    material_class = models.ForeignKey('MaterialClass', on_delete=models.CASCADE)
    category = TreeForeignKey('MaterialCategory', on_delete=models.CASCADE)
    targets = models.ManyToManyField(Target, related_name='material_targets')
    is_taxable = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    is_product = models.BooleanField(default=False)
    product_sell_price = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    material_sell_price = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    preferred_vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, blank=True, null=True)
    usage_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='usage_unit')
    retail_unit = models.ForeignKey(Unit, on_delete=models.CASCADE, related_name='retail_unit')
    documentation = models.FileField(upload_to='materials/documentation', blank=True, null=True)

    def __str__(self):
        return f'{self.name} | {self.brand.name}'

    class Meta:
        verbose_name = _('Material')
        verbose_name_plural = _('Materials')

    def get_absolute_url(self):
        return reverse_lazy('inventory:material_detail', kwargs={'pk': self.pk})


class MaterialCategory(MPTTModel):
    """
    Represents a category of materials that share common fields, properties, or characteristics.
    """
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=256)
    fields = GenericRelation(Field)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name', ]

    class Meta:
        verbose_name = _('Material Category')
        verbose_name_plural = _('Material Categories')

    def __str__(self):
        return f'{self.name}'


class MaterialClass(models.Model):
    """
    A material class is a group of materials that can be used interchangeably in the provision of a service.
    Each material class has a name and can include multiple materials, each with a priority order.
    """

    name = models.CharField(max_length=64)
    description = models.TextField()

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = _('Material Class')
        verbose_name_plural = _('Material Classes')


class MaterialField(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.TextField()

    def __str__(self):
        return f"{self.field.name}: {self.value}"

    class Meta:
        verbose_name = _('Material Field')
        verbose_name_plural = _('Material Fields')
        unique_together = ('material', 'field',)
