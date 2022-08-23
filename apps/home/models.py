# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='employee', default='', blank=True)
    location = models.CharField(max_length=30, blank=True, default='')
    birth_date = models.DateField(null=True, blank=True, default=None)

    class Meta:
        managed = True

class Shopper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        managed = True

class Consignor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        managed = True

@receiver(post_save, sender=User)
def create_user_extentions(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)
        Shopper.objects.create(user=instance)
        Consignor.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_extentions(sender, instance, **kwargs):
    instance.employee.save()
    instance.shopper.save()
    instance.consignor.save()