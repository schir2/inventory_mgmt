from django.db import models

from inventory.models.material import Material, MaterialClass
from inventory.models.target import Target
from inventory.models.warranty import WarrantyTemplate


class Service(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    targets = models.ManyToManyField(Target, related_name='service_targets')
    material_classes = models.ManyToManyField('MaterialClass', )
    required_materials = models.ManyToManyField(Material, related_name='services_with_required_materials', blank=True,
                                                through='RequiredServiceMaterial')
    suggested_materials = models.ManyToManyField(Material, related_name='services_with_suggested_materials', blank=True,
                                                 through='SuggestedServiceMaterial')
    products = models.ManyToManyField(Material, related_name='services_with_products', blank=True,
                                      through='ServiceProduct')
    warranty_template = models.ForeignKey(WarrantyTemplate, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class PricingScheme(models.Model):
    # TODO Define the properties for pricing scheme
    name = models.CharField(max_length=255)


class RequiredServiceMaterial(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.material} ({self.quantity})'


class SuggestedServiceMaterial(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.material} ({self.quantity})'


class ServiceProduct(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    product = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.product} ({self.quantity})'


class ServiceMaterialClass(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    material_class = models.ForeignKey(MaterialClass, on_delete=models.CASCADE)
