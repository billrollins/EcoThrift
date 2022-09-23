# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views


urlpatterns = [
    path('AddDepartment', views.pages, name='AddDepartment'),
    path('AddDropoff', views.pages, name='AddDropoff'),
    path('AddItem', views.pages, name='AddItem'),
    path('AddLiquidator', views.pages, name='AddLiquidator'),
    path('AddLocation', views.pages, name='AddLocation'),
    path('AddOrder', views.pages, name='AddOrder'),
    path('AddPosition', views.pages, name='AddPosition'),
    path('AddSection', views.pages, name='AddSection'),
    path('AddStore', views.pages, name='AddStore'),
    path('Dashboard', views.pages, name='Dashboard'),
    path('EditDepartment', views.pages, name='EditDepartment'),
    path('EditDropoff', views.pages, name='EditDropoff'),
    path('EditItem', views.pages, name='EditItem'),
    path('EditLiquidator', views.pages, name='EditLiquidator'),
    path('EditLocation', views.pages, name='EditLocation'),
    path('EditOrder', views.pages, name='EditOrder'),
    path('EditPosition', views.pages, name='EditPosition'),
    path('EditSection', views.pages, name='EditSection'),
    path('EditStore', views.pages, name='EditStore'),
    path('ViewDepartments', views.pages, name='ViewDepartments'),
    path('ViewDropoffs', views.pages, name='ViewDropoffs'),
    path('ViewItems', views.pages, name='ViewItems'),
    path('ViewLiquidators', views.pages, name='ViewLiquidators'),
    path('ViewLocations', views.pages, name='ViewLocations'),
    path('ViewOrders', views.pages, name='ViewOrders'),
    path('ViewPositions', views.pages, name='ViewPositions'),
    path('ViewSections', views.pages, name='ViewSections'),
    path('ViewStores', views.pages, name='ViewStores'),
    path('Delete', views.delete, name='delete'),
    path('', views.pages, name=''),
]