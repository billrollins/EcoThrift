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
from datetime import date, datetime
from string import ascii_uppercase
from decimal import Decimal
from phonenumber_field.modelfields import PhoneNumberField
from uuid import uuid4
import re

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
# Key/Value Functions
##################################################################################################################

def GET_KV_ARGS(s):
    args = {}
    if '=' in s:
        for _kv in s.split(';'):
            if '=' in _kv:
                kv = _kv.split('=')
                args[kv[0]] = kv[1]
    return args
    
def GET_KEYS(dct, keys):
    return dict((k, dct[k]) for k in keys if k in dct)

##################################################################################################################
# String Functions
##################################################################################################################

SLUGS = {
    '&' : '-AMS', '*' : '-ASR', "'" : '-APT', '@' : '-CCA',
    '%' : '-PCS', '^' : '-CFA', '+' : '-PLS', ':' : '-CLN',
    '"' : '-QTM', '?' : '-QSM', ',' : '-CMA', '`' : '-GAC',
    '~' : '-TLD', '!' : '-EXM', '#' : '-NBS', '$' : '-DLS',
    '(' : '-LPT', ')' : '-RPT', '_' : '-LOL', '-' : '-HPM',
    '=' : '-EQS', '{' : '-LCB', '}' : '-RCB', '|' : '-VTL',
    '[' : '-LSB', ']' : '-RSB', '\\' : '-RSD', ';' : '-SCN',
    '<' : '-LTS', '>' : '-GTS', '.' : '-FST', '/' : '-SLD'
}

def SLUGIFY(_str):
    for _char, _slug in SLUGS.items():
        _str = _str.replace(_char, _slug)
    return _str

def DESLUG(_str):
    for _char, _slug in SLUGS.items():
        _str = _str.replace(_slug, _char)
    return _str

def STR_FULL_NM(m):
    return f'{m.last_name}, {m.first_name}'

def STR_LOC_1(m):
    return f'{m.city}, {m.state}'

def STR_LOC_2(m):
    return f'{m.state} {m.city}'

    
##################################################################################################################
# Process Key Values
##################################################################################################################


TYPES = ['Form','Table']
def TYPE(str):
    for t in TYPES:
        if f'{t};' in f'{str};':
            return t
    return None

def DCT_FROM_GET(_get):
    dct = {}
    for kv in _get.split(f'?')[-1].split(';'):
        kv = kv.split('=')
        if len(kv)==2:
            k = DESLUG(kv[0])
            v = [ DESLUG(_v) for _v in kv[1].split(',') ]
            if len(v) == 1: 
                v = v[0]
            dct[k] =  v
    return dct

def DOUBLE_FORMAT(str, dict1, dict2):
    str = str.format(**dict1)
    str = re.sub('<<', '{', str)
    str = re.sub('>>', '}', str)
    return str.format(**dict2)

def GET_DCT_FROM_STR(prep_str):
    dct = {}
    for kv in prep_str.split('@@;'):
        kv = kv.split('@@=')
        print(kv)
        if len(kv)==2:
            dct[kv[0]] = kv[1].split('@@,') if '@@,' in kv[1] else kv[1]
    return None

def MAKE_DICT(obj):
    _dict = obj
    if type(_dict) != dict:
        try:            
            _dict = _dict.__dict__
        except:
            _dict = dict(obj)
    return _dict

def FORMAT(str, obj):
    format_dict = MAKE_DICT(obj)
    format_str = str.format(**format_dict)
    return format_str


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
    
PAGE_DESIGN = SITE_DESIGN['Page']
MODEL_DESIGN = SITE_DESIGN['Model']
FORM_DESIGN = SITE_DESIGN['Form']
TABLE_DESIGN = SITE_DESIGN['Table']
SIDEBAR = SITE_DESIGN['Sidebar']

##################################################################################################################
# Prices
##################################################################################################################

PRICE_DICT = {}
_prices = [50000, 47000, 44000, 41000, 38000, 35000, 32000, 29000, 26000, 23000, 20000, 18000, 16000, 14000, 12000, 11000, 10000, 9500, 9000, 8500, 8000, 7500, 7000, 6500, 6000, 5500, 5000, 4700, 4400, 4100, 3800, 3500, 3200, 2900, 2600, 2300, 2000, 1800, 1600, 1400, 1200, 1100, 1000, 950, 900, 850, 800, 750, 700, 650, 600, 550, 500, 470, 440, 410, 380, 350, 320, 290, 260, 230, 200, 180, 160, 140, 120, 110, 100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 47, 44, 41, 38, 35, 32, 29, 26, 23, 20, 18, 16, 14, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
for i in range(1,5):
    for c in ascii_uppercase:
        PRICE_DICT[f'{c}{i}'] = _prices
        _prices = _prices[1:] + _prices[:1]        

##################################################################################################################
# Choice Lists
##################################################################################################################

ORDER_CATEGORY_LIST = [
    ('APPAREL','APPAREL'),
    ('APPLIANCES - LARGE','APPLIANCES - LARGE'),
    ('APPLIANCES - SMALL','APPLIANCES - SMALL'),
    ('BIKES & RIDE ONS','BIKES & RIDE ONS'),
    ('CONSUMER ELECTRONICS','CONSUMER ELECTRONICS'),
    ('COOKWARE','COOKWARE'),
    ('DOMESTICS','DOMESTICS'),
    ('FOOD','FOOD'),
    ('FOOTWEAR','FOOTWEAR'),
    ('FURNITURE','FURNITURE'),
    ('GARDEN / PATIO','GARDEN / PATIO'),
    ('GENERAL MERCHANDISE','GENERAL MERCHANDISE'),
    ('HARDWARE','HARDWARE'),
    ('HEALTH & BEAUTY','HEALTH & BEAUTY'),
    ('HOME DECOR','HOME DECOR'),
    ('JEWELRY','JEWELRY'),
    ('LUGGAGE','LUGGAGE'),
    ('MAJOR APPLIANCES','MAJOR APPLIANCES'),
    ('MIXED LOTS','MIXED LOTS'),
    ('RUGS','RUGS'),
    ('SEASONAL','SEASONAL'),
    ('SPORTING GOODS','SPORTING GOODS'),
    ('TOOLS','TOOLS'),
    ('TOYS','TOYS'),
    ('TVS','TVS'),
    ('VACUUMS','VACUUMS')
]
EMAIL_PREFERENCES_LIST = [
    ('All Emails','All Emails'),
    ('No Emails','No Emails'),
]

DEPARTMENT_LIST = [
    ('Checkout','Checkout'),
    ('Expensive Items','ExpensiveItems'),
    ('General Items','GeneralItems'),
    ('Inventory','Inventory'),
    ('Kids Apparel','KidsApparel'),
    ('Large Items','LargeItems'),
    ('Processing','Processing'),
]

PID_LIST = [
    ('Drivers Liscense','DriversLiscense'),
    ('Passport','Passport'),
    ('Student ID','StudentID'),

]

CONDITION_LIST = [
    ('New - Brand New','BrandNew'),    
    ('New - Excellent','NewExcellent'),
    ('New - Very Good','NewVeryGood'),
    ('New - Good','NewGood'),
    ('New - Acceptable','NewAcceptable'),
    ('New - Poor','NewPoor'),
    ('New - Salvage','NewSalvage'),
    ('Used - Excellent','UsedExcellent'),
    ('Used - Very Good','UsedVeryGood'),
    ('Used - Good','UsedGood'),
    ('Used - Acceptable','UsedAcceptable'),
    ('Used - Poor','UsedPoor'),
    ('Used - Salvage','UsedSalvage'),
    ('Reject - Condition','Condition'),
    ('Reject - Dirty','Dirty'),
    ('Reject - MissingParts','MissingParts'),
    ('Reject - Violation','Violation')
]

TESTED_LIST = [
    ('Not Tested','NotTested'),    
    ('Tested - Works Perfect','WorksPerfect'),
    ('Tested - Works Okay','WorksOk'),
    ('Tested - Works Some Damage','SomeDamage'),
    ('Tested - Works Heavy Damage','HeavyDamage'),
    ('Tested - Repairable Light','RepairableLight'),
    ('Tested - Repairable Heavy','RepairableHeavy'),
    ('Tested - Salvage','Salvage')
]

STATUS_CHANGE_LIST = [
    ('Lost','Lost'),
    ('Stolen','Stolen'),
    ('Broken - Kept','BrokenKept'),
    ('Broken - Recycled','BrokenRecycled'),
    ('Broken - Disposed','BrokenDisposed'),
    ('Broken - Free','BrokenFree'),
    ('Removed - Donation','RemovedDonation'),
    ('Removed - Violation','RemovedViolation'),
    ('Removed - Returned','RemovedReturned'),
    ('Removed - Moved','RemovedMoved')
]

ST_LIST = [('AL','AL'),('AK','AK'),('AZ','AZ'),('AR','AR'),('CA','CA'),('CO','CO'),('CT','CT'),('DE','DE'),('FL','FL'),('GA','GA'),('HI','HI'),('ID','ID'),('IL','IL'),('IN','IN'),('IA','IA'),('KS','KS'),('KY','KY'),('LA','LA'),('ME','ME'),('MD','MD'),('MA','MA'),('MI','MI'),('MN','MN'),('MS','MS'),('MO','MO'),('MT','MT'),('NE','NE'),('NV','NV'),('NH','NH'),('NJ','NJ'),('NM','NM'),('NY','NY'),('NC','NC'),('ND','ND'),('OH','OH'),('OK','OK'),('OR','OR'),('PA','PA'),('RI','RI'),('SC','SC'),('SD','SD'),('TN','TN'),('TX','TX'),('UT','UT'),('VT','VT'),('VA','VA'),('WA','WA'),('WV','WV'),('WI','WI'),('WY','WY')]
STATE_LIST = [('Alabama','Alabama'),('Alaska','Alaska'),('Arizona','Arizona'),('Arkansas','Arkansas'),('California','California'),('Colorado','Colorado'),('Connecticut','Connecticut'),('Delaware','Delaware'),('Florida','Florida'),('Georgia','Georgia'),('Hawaii','Hawaii'),('Idaho','Idaho'),('Illinois','Illinois'),('Indiana','Indiana'),('Iowa','Iowa'),('Kansas','Kansas'),('Kentucky','Kentucky'),('Louisiana','Louisiana'),('Maine','Maine'),('Maryland','Maryland'),('Massachusetts','Massachusetts'),('Michigan','Michigan'),('Minnesota','Minnesota'),('Mississippi','Mississippi'),('Missouri','Missouri'),('Montana','Montana'),('Nebraska','Nebraska'),('Nevada','Nevada'),('New Hampshire','New Hampshire'),('New Jersey','New Jersey'),('New Mexico','New Mexico'),('New York','New York'),('North Carolina','North Carolina'),('North Dakota','North Dakota'),('Ohio','Ohio'),('Oklahoma','Oklahoma'),('Oregon','Oregon'),('Pennsylvania','Pennsylvania'),('Rhode Island','Rhode Island'),('South Carolina','South Carolina'),('South Dakota','South Dakota'),('Tennessee','Tennessee'),('Texas','Texas'),('Utah','Utah'),('Vermont','Vermont'),('Virginia','Virginia'),('Washington','Washington'),('West Virginia','West Virginia'),('Wisconsin','Wisconsin'),('Wyoming','Wyoming')]

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