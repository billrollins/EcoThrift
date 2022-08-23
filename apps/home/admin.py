# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin

# Register your models here.

from .models import Employee, Consignor, Shopper

admin.site.register(Employee)
admin.site.register(Consignor)
admin.site.register(Shopper)
