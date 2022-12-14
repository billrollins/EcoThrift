from django import forms, template
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.template import loader
from django.utils.deconstruct import deconstructible
from django.utils.safestring import mark_safe

import os
import pandas as pd
import numpy as np
from datetime import date, datetime, timedelta
from string import ascii_uppercase
from decimal import Decimal
from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4
import re

from copy import copy, deepcopy

##################################################################################################################
# Directories and Files
##################################################################################################################

PROJ_DIR = os.getcwd()
APPS_DIR = os.path.join(PROJ_DIR, 'apps')
HOME_DIR = os.path.join(APPS_DIR, 'home')
STATIC_DIR = os.path.join(APPS_DIR, 'static')
DATA_DIR = os.path.join(STATIC_DIR, 'assets', 'data')

##################################################################################################################
# Eco-Thrift Colors
##################################################################################################################

ET_COLORS = {
    'ET_GreenLight':    "#8ac33f",
    'ET_GreenDark':     "#53863f",
    'ET_Green':         "#70a63f",
    'ET_Yellow':        "#eec93a",
    'ET_YellowLight':   "#f5e597",
    'ET_YellowDark':    "#d29401",
    'ET_White':         "#f6f6f6",
    'ET_Black':         "#000405",
}

##################################################################################################################
# Constants
##################################################################################################################

DEFAULT_END_DATE = date(9999,12,31)
DEFAULT_START_DATE = date(1,1,1)
STATE_DICT = {'AL':'Alabama', 'AK':'Alaska', 'AZ':'Arizona', 'AR':'Arkansas', 'CA':'California', 'CO':'Colorado', 'CT':'Connecticut', 'DE':'Delaware', 'FL':'Florida', 'GA':'Georgia', 'HI':'Hawaii', 'ID':'Idaho', 'IL':'Illinois', 'IN':'Indiana', 'IA':'Iowa', 'KS':'Kansas', 'KY':'Kentucky', 'LA':'Louisiana', 'ME':'Maine', 'MD':'Maryland', 'MA':'Massachusetts', 'MI':'Michigan', 'MN':'Minnesota', 'MS':'Mississippi', 'MO':'Missouri', 'MT':'Montana', 'NE':'Nebraska', 'NV':'Nevada', 'NH':'New Hampshire', 'NJ':'New Jersey', 'NM':'New Mexico', 'NY':'New York', 'NC':'North Carolina', 'ND':'North Dakota', 'OH':'Ohio', 'OK':'Oklahoma', 'OR':'Oregon', 'PA':'Pennsylvania', 'RI':'Rhode Island', 'SC':'South Carolina', 'SD':'South Dakota', 'TN':'Tennessee', 'TX':'Texas', 'UT':'Utah', 'VT':'Vermont', 'VA':'Virginia', 'WA':'Washington', 'WV':'West Virginia', 'WI':'Wisconsin', 'WY':'Wyoming'}

##################################################################################################################
# Icons
##################################################################################################################

def ILIGHT(icon):
    return icon.replace('fa-regular', 'fa-light')

def ISOLID(icon):
    return icon.replace('fa-regular', 'fa-solid')

# Graphics
ICON_TRASH = 'fa-regular fa-trash'
ICON_CLOCK = 'fa-regular fa-clock'
ICON_COUCH = 'fa-regular fa-couch'
ICON_BUS_TIME = 'fa-regular fa-business-time'
ICON_CHESS = 'fa-regular fa-chess'
ICON_DATABASE = 'fa-regular fa-database'

# Geometric
ICON_SQR_MINUS = 'fa-regular fa-square-minus'
ICON_SQR_PLUS = 'fa-regular fa-square-plus'

# Characters
ICON_CHECK = 'fa-solid fa-check'
ICON_MINUS = 'fa-solid fa-minus'
ICON_PLUS = 'fa-solid fa-plus'
ICON_EXCLAMATION = 'fa-solid fa-exclamation'

##################################################################################################################
# String Functions
##################################################################################################################

def STR_FULL_NM(m):
    return f'{m.last_name}, {m.first_name}'

def STR_LOC_1(m):
    return f'{m.city}, {m.state}'

def STR_LOC_2(m):
    return f'{m.state} {m.city}'

def STR_DATE(d):
    return d.isoformat()

def STR_TODAY(delta=timedelta(0)):
    if type(delta) == int:
        delta = timedelta(days=delta)
    return STR_DATE(date.today() + delta)
    
##################################################################################################################
# Key/Value or Dictionary Functions
##################################################################################################################

def MAKE_DICT(obj):
    _dict = obj
    i = 0 
    while type(_dict) != dict:
        try:
            # Forms have a get_dict() function which includes the model pk
            if i == 0:
                _dict = _dict.get_dict()
            elif i == 1:
                _dict = dict(obj)
            elif i==2:
                _dict = _dict.__dict__
            else:
                _dict = globals()
        except:
            i += 1
            if i > 4: return False
    return _dict

def FORMAT(str, obj):
    format_dict = MAKE_DICT(obj)
    format_str = str.format(**format_dict)
    return format_str

def DICT_REMOVE_EMPTY(dict):
    for k in [k for k, v in dict.items() if not v]: del dict[k] 
    return dict

def DICTS_FORMAT(str, dicts, cycles=3):
    for z in range(cycles):
        for dict_name, dict_kvs in dicts.items():        
            for k,v in dict_kvs.items(): 
                str = str.replace(f'{dict_name}[{k}]', f'{v}')
    return str

##################################################################################################################
# Notifications
##################################################################################################################

receiver_variable = None
notifications = []

def add_notification(icon='', heading='', body='', id=None):
    global notifications
    
    # https://www.creative-tim.com/learning-lab/nextjs/icons/argon-dashboard
    _icons = {
        '': 'ni-air-baloon text-success',
        'add': 'ni-fat-add text-success',
        'save': 'ni-cloud-upload-96 text-info',
        'info': 'ni-notification-70 text-info',
        'warn': 'ni-air-baloon text-warning',
        'delete': 'ni-fat-delete text-danger'
    }

    # notif_icon, notif_head, notif_body, notif_id
    newNotification = [
        _icons[icon],
        heading,
        body,
        id if id else f'ntf_{len(notifications)}'
    ] 
    notifications.append(newNotification)
    return

def LOAD_NOTIFICATIONS():
    global notifications
    notifs = notifications
    notifications = []
    return notifs

##################################################################################################################
# Site Design - Models, Forms, Pages
##################################################################################################################

def _get_site_design(_design_list):
    site_design = {}
    for design in _design_list:
        design_df = pd.read_pickle(os.path.join(DATA_DIR, f'{design[0]}.pkl'))
        design_nm = ''.join([d.capitalize() for d in design[0].split('_')])
        design_dct = {}

        if len(design) == 1:
            design_dct = [dict(r) for _, r in design_df.iterrows()]
        else:
            detail_nm = design[1].split('_')[1].capitalize() + "s"
            detail_df = pd.read_pickle(os.path.join(DATA_DIR, f'{design[1]}.pkl'))
            design_dct = design_df.set_index(design_nm, drop=True).T.to_dict()
            for k in design_dct:
                thisDetail = (
                    detail_df[detail_df[design_nm]==k]
                    .drop(design_nm, axis=1)
                )
                design_dct[k][detail_nm] = [dict(r) for _, r in thisDetail.iterrows()]

        site_design[design_nm] = design_dct
    return site_design

SITE_DESIGN = _get_site_design([
    ['sidebar'],
    ['page','page_element'],
    ['meta_form'],
    ['form','form_field'],
    ['model','model_field'],
    ['table','table_field']
])
    
SIDEBAR = [
    {'Menu': 'Home', 'SubMenu': 'Dashboard', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'Dashboard', 'Icon': 'fas fa-couch'},
    {'Menu': '', 'SubMenu': 'Profile', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'MyProfile', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'TimeClock', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'TimeClock', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Calendar', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'MyCalendar', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Add Event', 'Text': '', 'EndSub': 'End', 'EndMenu': 'End', 'Page': 'AddEvent', 'Icon': ''},
    {'Menu': 'Operations', 'SubMenu': 'Inventory', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewInventory', 'Icon': 'fas fa-business-time'},
    {'Menu': '', 'SubMenu': 'Orders', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewOrders', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'DropOff', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewDropoffs', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Items', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewItems', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Check-In', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'CheckIn', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Check-Out', 'Text': '', 'EndSub': 'End', 'EndMenu': 'End', 'Page': 'CheckOut', 'Icon': ''},
    {'Menu': 'Management', 'SubMenu': 'Employees', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewEmployee', 'Icon': 'fas fa-chess'},
    {'Menu': '', 'SubMenu': 'Consignors', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewConsignors', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Liquidators', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewLiquidators', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Schedule', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewSchedule', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Vacation', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewVacation', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Drawers', 'Text': '', 'EndSub': 'End', 'EndMenu': 'End', 'Page': 'ViewDrawers', 'Icon': ''},
    {'Menu': 'Database', 'SubMenu': 'Stores', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewStores', 'Icon': 'fas fa-database'},
    {'Menu': '', 'SubMenu': 'Departments', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewDepartments', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Positions', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewPositions', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Sections', 'Text': '', 'EndSub': 'End', 'EndMenu': '', 'Page': 'ViewSections', 'Icon': ''},
    {'Menu': '', 'SubMenu': 'Locations', 'Text': '', 'EndSub': 'End', 'EndMenu': 'End', 'Page': 'ViewLocations', 'Icon': ''}
]

{'AddConsignor': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Consignors', 'Text': 'Add Consignor', 'Heading': 'Add Consignor Below', 'SubHeading': '<a href="/ViewConsignors" class="text-primary">View Consignors</a> to edit existing consignor.', 'Elements': []}, 'AddDepartment': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Department', 'Menu': 'Database', 'SubMenu': 'Departments', 'Text': 'Add Department', 'Heading': 'Add Department Below', 'SubHeading': '<a href="/ViewDepartments" class="text-primary">View Departments</a> to edit existing department.', 'Elements': [{'Element': 'AddDepartmentForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddDrawer': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Drawers', 'Text': 'Add Drawer', 'Heading': 'Add Drawer Below', 'SubHeading': '<a href="/ViewDrawers" class="text-primary">View Drawers</a> to edit existing drawer.', 'Elements': []}, 'AddDropoff': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Dropoff', 'Menu': 'Operations', 'SubMenu': 'DropOff', 'Text': 'Add DropOff', 'Heading': 'Add DropOff Below', 'SubHeading': '<a href="/ViewDropoffs" class="text-primary">View DropOffs</a> to edit existing dropoff.', 'Elements': [{'Element': 'AddDropoffForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddEmployee': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Employees', 'Text': 'Add Employee', 'Heading': 'Add Employee Below', 'SubHeading': '<a href="/ViewEmployee" class="text-primary">View Employees</a> to edit existing employee.', 'Elements': []}, 'AddInventory': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Operations', 'SubMenu': 'Inventory', 'Text': 'Add Inventory', 'Heading': 'Add Inventory Below', 'SubHeading': '<a href="/ViewInventory" class="text-primary">View Inventory</a> to edit existing inventory.', 'Elements': []}, 'AddLiquidator': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Liquidator', 'Menu': 'Management', 'SubMenu': 'Liquidators', 'Text': 'Add Liquidator', 'Heading': 'Add Liquidator Below', 'SubHeading': '<a href="/ViewLiquidators" class="text-primary">View Liquidators</a> to edit existing liquidator.', 'Elements': [{'Element': 'AddLiquidatorForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddLocation': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Location', 'Menu': 'Database', 'SubMenu': 'Locations', 'Text': 'Add Location', 'Heading': 'Add Location Below', 'SubHeading': '<a href="/ViewLocations" class="text-primary">View Locations</a> to edit existing location.', 'Elements': [{'Element': 'AddLocationForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddOrder': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Order', 'Menu': 'Operations', 'SubMenu': 'Orders', 'Text': 'Add Order', 'Heading': 'Add Order Below', 'SubHeading': '<a href="/ViewOrders" class="text-primary">View Orders</a> to edit existing order.', 'Elements': [{'Element': 'AddOrderForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddPosition': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Position', 'Menu': 'Database', 'SubMenu': 'Positions', 'Text': 'Add Position', 'Heading': 'Add Position Below', 'SubHeading': '<a href="/ViewPositions" class="text-primary">View Positions</a> to edit existing position.', 'Elements': [{'Element': 'AddPositionForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddSchedule': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Schedule', 'Text': 'Add Schedule', 'Heading': 'Add Schedule Below', 'SubHeading': '<a href="/ViewSchedule" class="text-primary">View Schedules</a> to edit existing schedule.', 'Elements': []}, 'AddSection': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Section', 'Menu': 'Database', 'SubMenu': 'Sections', 'Text': 'Add Section', 'Heading': 'Add Section Below', 'SubHeading': '<a href="/ViewSections" class="text-primary">View Sections</a> to edit existing section.', 'Elements': [{'Element': 'AddSectionForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddStore': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Add Store', 'Menu': 'Database', 'SubMenu': 'Stores', 'Text': 'Add Store', 'Heading': 'Add Store Below', 'SubHeading': '<a href="/ViewStores" class="text-primary">View Stores</a> to edit existing store.', 'Elements': [{'Element': 'AddStoreForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'AddVacation': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Vacation', 'Text': 'Add Vacation', 'Heading': 'Add Vacation Below', 'SubHeading': '<a href="/ViewVacation" class="text-primary">View Vacation</a> to edit existing vacation.', 'Elements': []}, 'EditConsignor': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Consignors', 'Text': 'Edit Consignor', 'Heading': 'Edit Consignor Below', 'SubHeading': 'or <a href="/ViewConsignors" class="text-primary">View Consignors</a>.', 'Elements': []}, 'EditDepartment': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Department', 'Menu': 'Database', 'SubMenu': 'Departments', 'Text': 'Edit Department', 'Heading': 'Edit Department Below', 'SubHeading': 'or <a href="/ViewDepartments" class="text-primary">View Departments</a>.', 'Elements': [{'Element': 'EditDepartmentForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditDrawer': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Drawers', 'Text': 'Edit Drawer', 'Heading': 'Edit Drawer Below', 'SubHeading': 'or <a href="/ViewDrawers" class="text-primary">View Drawers</a>.', 'Elements': []}, 'EditDropoff': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Dropoff', 'Menu': 'Operations', 'SubMenu': 'DropOff', 'Text': 'Edit DropOff', 'Heading': 'Edit DropOff Below', 'SubHeading': 'or <a href="/ViewDropoffs" class="text-primary">View DropOffs</a>.', 'Elements': [{'Element': 'EditDropoffForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditEmployee': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Employees', 'Text': 'Edit Employee', 'Heading': 
'Edit Employee Below', 'SubHeading': 'or <a href="/ViewEmployee" class="text-primary">View Employees</a>.', 'Elements': []}, 'EditInventory': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Operations', 'SubMenu': 'Inventory', 'Text': 'Edit Inventory', 'Heading': 'Edit Inventory Below', 'SubHeading': 'or <a href="/ViewInventory" class="text-primary">View Inventory</a>.', 'Elements': []}, 'EditLiquidator': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Liquidator', 'Menu': 'Management', 'SubMenu': 'Liquidators', 'Text': 'Edit Liquidator', 'Heading': 'Edit Liquidator Below', 'SubHeading': 'or <a href="/ViewLiquidators" class="text-primary">View Liquidators</a>.', 'Elements': [{'Element': 'EditLiquidatorForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditLocation': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Location', 'Menu': 'Database', 'SubMenu': 'Locations', 'Text': 'Edit Location', 'Heading': 'Edit Location Below', 'SubHeading': 'or <a href="/ViewLocations" class="text-primary">View Locations</a>.', 'Elements': [{'Element': 'EditLocationForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditOrder': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Order', 'Menu': 'Operations', 'SubMenu': 'Orders', 'Text': 'Edit Order', 'Heading': 'Edit Order Below', 'SubHeading': 'or <a href="/ViewOrders" class="text-primary">View Orders</a>.', 'Elements': [{'Element': 'EditOrderForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditPosition': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Edit Position', 'Menu': 'Database', 'SubMenu': 'Positions', 'Text': 'Edit Position', 'Heading': 'Edit Position Below', 'SubHeading': 'or <a href="/ViewPositions" class="text-primary">View Positions</a>.', 'Elements': [{'Element': 'EditPositionForm', 'Type': 'Form', 'RowCode': 'Both', 'JavaScript': ''}]}, 'EditSchedule': {'Type': 'Basic', 'Template': 'home/base-custom.html', 'Title': 'Dashboard', 'Menu': 'Management', 'SubMenu': 'Schedule', 'Text': 'Edit Schedule', 'Heading': 'Edit Schedule Below', 'SubHeading': 'or <a href="/ViewSc
PAGE_DESIGN = SITE_DESIGN['Page']
META_FORM_DESIGN = SITE_DESIGN['MetaForm']
FORM_DESIGN = SITE_DESIGN['Form']
MODEL_DESIGN = SITE_DESIGN['Model']
TABLE_DESIGN = SITE_DESIGN['Table']

##################################################################################################################
# Prices
##################################################################################################################

ECO_OPEN_DATE = date(2022, 10, 31)
ECO_PRICE_COUNT = 104
ECO_PRICES = np.array([    
    1,     2,     3,     4,     5,     6,     7,     8,     9,
    10,    11,    12,    14,    16,    18,    20,    23,    26,
    29,    32,    35,    38,    41,    44,    47,    50,    55,
    60,    65,    70,    75,    80,    85,    90,    95,   100,
    110,   120,   140,   160,   180,   200,   230,   260,   290,
    320,   350,   380,   410,   440,   470,   500,   550,   600,
    650,   700,   750,   800,   850,   900,   950,  1000,  1100,
    1200,  1400,  1600,  1800,  2000,  2300,  2600,  2900,  3200,
    3500,  3800,  4100,  4400,  4700,  5000,  5500,  6000,  6500,
    7000,  7500,  8000,  8500,  9000,  9500, 10000, 11000, 12000,
    14000, 16000, 18000, 20000, 23000, 26000, 29000, 32000, 35000,
    38000, 41000, 44000, 47000, 50000
])

def GET_TODAYS_PRICES():
    _dict, _reverse_dict = {}, {}
    _prices = np.sort(ECO_PRICES)[::-1]
    delta_days = (date.today() - ECO_OPEN_DATE).days
    price_delta = delta_days // 7
    
    for i in range(1,5):
        for c in ascii_uppercase:
            price_delta = price_delta % ECO_PRICE_COUNT
            lbl, price = f'{c}{i}', ECO_PRICES[price_delta]  
            _dict[lbl] = price
            _reverse_dict[price] = lbl
            price_delta += 1
    
    return _dict, _reverse_dict

PRICE_DICT, REVERSE_PRICE_DICT = GET_TODAYS_PRICES()

def GET_PRICE_ARRAY(from_price):
    _i = np.searchsorted(ECO_PRICES, from_price)
    return np.concatenate([ECO_PRICES[_i:], ECO_PRICES[:_i]])

##################################################################################################################
# Choice Lists
##################################################################################################################

PRICE_LIST = [(Decimal(i*1.00), f'{i:,.02f}') for i in ECO_PRICES]

LOCATION_LIST = []

def _SET_LOCATION_LIST(LocationClass):
    loc = np.array([[l.section.name, l.label] for l in LocationClass.objects.all()])
    loc = loc[loc[:,0].argsort()]
    return [(f'{l[0]}_{l[1]}', f'{l[0]} - {l[1]}') for l in loc]

ORDER_CATEGORY_LIST = [
    ('APPAREL', 'APPAREL'),
    ('APPLIANCES - LARGE', 'APPLIANCES - LARGE'),
    ('APPLIANCES - SMALL', 'APPLIANCES - SMALL'),
    ('BIKES & RIDE ONS', 'BIKES & RIDE ONS'),
    ('CONSUMER ELECTRONICS', 'CONSUMER ELECTRONICS'),
    ('COOKWARE', 'COOKWARE'),
    ('DOMESTICS', 'DOMESTICS'),
    ('FOOD', 'FOOD'),
    ('FOOTWEAR', 'FOOTWEAR'),
    ('FURNITURE', 'FURNITURE'),
    ('GARDEN / PATIO', 'GARDEN / PATIO'),
    ('GENERAL MERCHANDISE', 'GENERAL MERCHANDISE'),
    ('HARDWARE', 'HARDWARE'),
    ('HEALTH & BEAUTY', 'HEALTH & BEAUTY'),
    ('HOME DECOR', 'HOME DECOR'),
    ('JEWELRY', 'JEWELRY'),
    ('LUGGAGE', 'LUGGAGE'),
    ('MAJOR APPLIANCES', 'MAJOR APPLIANCES'),
    ('MIXED LOTS', 'MIXED LOTS'),
    ('RUGS', 'RUGS'),
    ('SEASONAL', 'SEASONAL'),
    ('SPORTING GOODS', 'SPORTING GOODS'),
    ('TOOLS', 'TOOLS'),
    ('TOYS', 'TOYS'),
    ('TVS', 'TVS'),
    ('VACUUMS', 'VACUUMS'),
]
EMAIL_PREFERENCES_LIST = [
    ('All Emails', 'All Emails'),
    ('No Emails', 'No Emails'),
]

DEPARTMENT_LIST = [
    ('Checkout', 'Checkout'),
    ('ExpensiveItems', 'Expensive Items'),
    ('GeneralItems', 'General Items'),
    ('Inventory', 'Inventory'),
    ('KidsApparel', 'Kids Apparel'),
    ('LargeItems', 'Large Items'),
    ('Processing', 'Processing'),
]

PID_LIST = [
    ('DriversLiscense', 'Drivers Liscense'),
    ('Passport', 'Passport'),
    ('StudentID', 'Student ID'),

]

CONDITION_LIST = [
    ('BrandNew', 'New - Brand New'),
    ('NewExcellent', 'New - Excellent'),
    ('NewVeryGood', 'New - Very Good'),
    ('NewGood', 'New - Good'),
    ('NewAcceptable', 'New - Acceptable'),
    ('NewPoor', 'New - Poor'),
    ('NewSalvage', 'New - Salvage'),
    ('UsedExcellent', 'Used - Excellent'),
    ('UsedVeryGood', 'Used - Very Good'),
    ('UsedGood', 'Used - Good'),
    ('UsedAcceptable', 'Used - Acceptable'),
    ('UsedPoor', 'Used - Poor'),
    ('UsedSalvage', 'Used - Salvage'),
    ('Condition', 'Reject - Condition'),
    ('Dirty', 'Reject - Dirty'),
    ('MissingParts', 'Reject - MissingParts'),
    ('Violation', 'Reject - Violation')
]

TESTED_LIST = [
    ('NotTested', 'Not Tested'),
    ('WorksPerfect', 'Tested - Works Perfect'),
    ('WorksOk', 'Tested - Works Okay'),
    ('SomeDamage', 'Tested - Works Some Damage'),
    ('HeavyDamage', 'Tested - Works Heavy Damage'),
    ('RepairableLight', 'Tested - Repairable Light'),
    ('RepairableHeavy', 'Tested - Repairable Heavy'),
    ('Salvage', 'Tested - Salvage'),
]

STATUS_CHANGE_LIST = [    
    ('CheckedIn', 'Checked-In'),
    ('Delivered', 'Delivered'),    
    ('Undelivered', 'Undelivered'),
    ('Unfulfilled', 'Unfulfilled'),
    ('Lost', 'Lost'),
    ('Stolen', 'Stolen'),
    ('BrokenKept', 'Broken - Kept'),
    ('BrokenRecycled', 'Broken - Recycled'),
    ('BrokenDisposed', 'Broken - Disposed'),
    ('BrokenFree', 'Broken - Free'),
    ('RemovedDonation', 'Removed - Donation'),
    ('RemovedViolation', 'Removed - Violation'),
    ('RemovedReturned', 'Removed - Returned'),
    ('RemovedMoved', 'Removed - Moved'),
]

ADD_ITEM_OPTIONS_LIST = [    
    ('NotCheckedIn', 'Not Checked In'),
    ('RecentlyAdded', 'Recently Added'),    
    ('RecentlySold', 'Recently Sold'),
    ('BackstockQuantity', 'Backstock Quantity'),
]

ST_LIST = [('AL','AL'),('AK','AK'),('AZ','AZ'),('AR','AR'),('CA','CA'),('CO','CO'),('CT','CT'),('DE','DE'),('FL','FL'),('GA','GA'),('HI','HI'),('ID','ID'),('IL','IL'),('IN','IN'),('IA','IA'),('KS','KS'),('KY','KY'),('LA','LA'),('ME','ME'),('MD','MD'),('MA','MA'),('MI','MI'),('MN','MN'),('MS','MS'),('MO','MO'),('MT','MT'),('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),('NM','NM'),('NY','NY'),('NC','NC'),('ND','ND'),('OH','OH'),('OK','OK'),('OR','OR'),('PA','PA'),('RI','RI'),('SC','SC'),('SD','SD'),('TN','TN'),('TX','TX'),('UT','UT'),('VT','VT'),('VA','VA'),('WA','WA'),('WV','WV'),('WI','WI'),('WY','WY')]
STATE_LIST = [('Alabama','Alabama'),('Alaska','Alaska'),('Arizona','Arizona'),('Arkansas','Arkansas'),('California','California'),('Colorado','Colorado'),('Connecticut','Connecticut'),('Delaware','Delaware'),('Florida','Florida'),('Georgia','Georgia'),('Hawaii','Hawaii'),('Idaho','Idaho'),('Illinois','Illinois'),('Indiana','Indiana'),('Iowa','Iowa'),('Kansas','Kansas'),('Kentucky','Kentucky'),('Louisiana','Louisiana'),('Maine','Maine'),('Maryland','Maryland'),('Massachusetts','Massachusetts'),('Michigan','Michigan'),('Minnesota','Minnesota'),('Mississippi','Mississippi'),('Missouri','Missouri'),('Montana','Montana'),('Nebraska','Nebraska'),('Nevada','Nevada'),('New Hampshire','New Hampshire'),('New Jersey','New Jersey'),('New Mexico','New Mexico'),('New York','New York'),('North Carolina','North Carolina'),('North Dakota','North Dakota'),('Ohio','Ohio'),('Oklahoma','Oklahoma'),('Oregon','Oregon'),('Pennsylvania','Pennsylvania'),('Rhode Island','Rhode Island'),('South Carolina','South Carolina'),('South Dakota','South Dakota'),('Tennessee','Tennessee'),('Texas','Texas'),('Utah','Utah'),('Vermont','Vermont'),('Virginia','Virginia'),('Washington','Washington'),('West Virginia','West Virginia'),('Wisconsin','Wisconsin'),('Wyoming','Wyoming')]


##################################################################################################################
# Liquidation - Manifests

##################################################################################################################

MANIFEST_HEADING_FIELDS = [
    ('Amazon 1', {'item description' : 'description', 'gl description' : 'department', 'product class' : 'item_class', 'category' : 'category', 'subcategory' : 'subcategory', 'qty' : 'units', 'unit retail' : 'unit_retail', 'asin' : '', 'ext. retail' : '', 'inventory reference id' : '', 'shipmentid' : '', 'shipmentitemid' : '', 'shipped qty' : '', 'unfulfilled qty' : '', 'upc' : ''}),
    ('B-Stock 1', {'item description' : 'description', 'manufacturer' : 'brand', 'model' : 'model', 'qty' : 'units', 'retail per unit' : 'unit_retail', 'carrier' : '', 'expiration date' : '', 'memory' : '', 'total retail' : '', 'upc' : ''}),
    ('Costco 1', {'item description' : 'description', 'department' : 'department', 'category' : 'category', 'brand' : 'brand', 'qty' : 'units', 'unit retail' : 'unit_retail', 'category code' : '', 'dept. code' : '', 'ext. retail' : '', 'item #' : '', 'lot #' : ''}),
    ('Home Depot 1', {'item description' : 'description', 'department' : 'department', 'product class' : 'item_class', 'category' : 'category', 'subcategory' : 'subcategory', 'brand' : 'brand', 'model' : 'model', 'qty' : 'units', 'unit retail' : 'unit_retail', 'ext. retail' : '', 'order #' : '', 'sb #' : '', 'sku' : '', 'upc' : ''}),
    ('Target 1', {'item description' : 'description', 'department' : 'department', 'product class' : 'item_class', 'category' : 'category', 'subcategory' : 'subcategory', 'brand' : 'brand', 'qty' : 'units', 'retail' : 'unit_retail', 'item' : '', 'ext. retail' : '', 'pallet id' : '', 'upc' : ''}),
    ('Target 2', {'item description' : 'description', 'sep cat' : 'department', 'product type' : 'item_class', 'category' : 'category', 'item model' : 'model', 'qty' : 'units', 'retail' : 'unit_retail', 'cat.' : '', 'cat. desc.' : '', 'container type' : '', 'ext. retail' : '', 'item' : '', 'item dep id' : '', 'origin' : '', 'pallet' : '', 'warehouse code' : ''}),
    ('Walmart 1', {'item description' : 'description', 'department' : 'department', 'subcategory' : 'category', 'model' : 'model', 'qty' : 'units', 'unit retail' : 'unit_retail', 'upc' : '', 'ext. retail' : '', 'unit weight' : '', 'pallet id' : '', 'pallet name' : '', 'pallet type' : ''})
]

def GET_MANIFEST_FIELDS(field_list):
    heading_fields, match_cnt, match_pct, heading_template = {}, 0, 0, ''
    for _d, h in MANIFEST_HEADING_FIELDS:
        _match_cnt = len([1 for f in field_list if f.lower() in h.keys()])
        _match_pct = _match_cnt / len(h.keys())
        replace = _match_cnt > match_cnt
        if _match_cnt == match_cnt: replace = _match_pct > match_pct
        if replace:
            heading_fields, match_cnt, match_pct, heading_template = h, _match_cnt, _match_pct, _d
    
    return heading_template, DICT_REMOVE_EMPTY(heading_fields)

##################################################################################################################
# Google Storage Directories
##################################################################################################################

# Giving files random names
@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)

# File directories on google cloud storage
EMP_IMG = PathAndRename("user-employee-image")
SHP_WAV = PathAndRename("user-shopper-waiver")
CON_WAV = PathAndRename("user-consignor-waiver")
CON_IMG = PathAndRename("user-consignor-image")
CON_PID = PathAndRename("user-consignor-pid")
ORD_IMG = PathAndRename("order-image")
ORD_MAN = PathAndRename("order-manifest")
ORD_POD = PathAndRename("order-pod")
DRP_AGR = PathAndRename("dropoff-agreement")
ITM_IMG = PathAndRename("item-image")