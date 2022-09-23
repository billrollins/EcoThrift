from django import forms
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.db import models
from django.db.models import Model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import HttpResponse, HttpRequest, JsonResponse
from django.shortcuts import redirect

from django import template
from django.template import loader

from django.utils.deconstruct import deconstructible
from django.utils.safestring import mark_safe

from asyncio.proactor_events import _ProactorBaseWritePipeTransport
from dataclasses import field
from unittest.mock import NonCallableMagicMock

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

def STR_FULL_NM(m):
    return f'{m.last_name}, {m.first_name}'

def STR_LOC_1(m):
    return f'{m.city}, {m.state}'

def STR_LOC_2(m):
    return f'{m.state} {m.city}'

def DOUBLE_FORMAT(str, dict1, dict2):
    str = str.format(**dict1)
    str = re.sub('<<', '{', str)
    str = re.sub('>>', '}', str)
    return str.format(**dict2)

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


def load_notifications():
    global notifications
    notifs = notifications
    notifications = []
    return notifs

##################################################################################################################
# Site Design - File Names
##################################################################################################################

SD_MODELS_FN = os.path.join(DATA_DIR, 'models.pkl')
SD_MODEL_FIELDS_FN = os.path.join(DATA_DIR, 'model_fields.pkl')

SD_META_FORMS_FN = os.path.join(DATA_DIR, 'meta_forms.pkl')
SD_FORMS_FN = os.path.join(DATA_DIR, 'forms.pkl')
SD_FORM_FIELDS_FN = os.path.join(DATA_DIR, 'form_fields.pkl')

SD_TABLES_FN = os.path.join(DATA_DIR, 'tables.pkl')
SD_TABLE_FIELDS_FN = os.path.join(DATA_DIR, 'table_fields.pkl')

SD_PAGES_FN = os.path.join(DATA_DIR, 'pages.pkl')
SD_PAGE_ELEMENTS_FN = os.path.join(DATA_DIR, 'page_elements.pkl')

##################################################################################################################
# Site Design - Models, Forms, Pages
##################################################################################################################

def _get_details(nm, _det, i, fn, det_fn):
    res = {}
    det_df = pd.read_pickle(det_fn)
    for _, x in pd.read_pickle(fn).iterrows():
        _x = x[i]
        res[_x] = dict(x)
        res[_x][_det] = [dict(det) for _, det in det_df[det_df[nm] == x[i]].iterrows()]
    return res

def GET_FORM_FIELDS(form_design):
    fields = form_design['Fields']
    field_attrs = []
    field_struct, field_row, row_idx, col_idx = [], [], 0, 0
    struct_keys = ['Name', 'Heading', 'Label', 'Size']
    attr_keys = ['Class','Type']
    for f in fields:
      attrs = GET_KEYS(f, attr_keys)
      if f['Attrs']:
        attrs.update(**GET_KV_ARGS(f['Attrs']))
      field_attrs += [(f['Name'], attrs, f['Template'])]
      if f['Row'] > row_idx:
        field_struct += [field_row]
        row_idx = f['Row']
        field_row = []
      field_row += [GET_KEYS(f, struct_keys)]
    field_struct += [field_row]
    return field_struct, field_attrs

PAGE_DESIGN = _get_details('Page', 'Elements', 'URL', SD_PAGES_FN, SD_PAGE_ELEMENTS_FN)
MODEL_DESIGN = _get_details('Model', 'Fields', 'Name', SD_MODELS_FN, SD_MODEL_FIELDS_FN)
FORM_DESIGN = _get_details('Form', 'Fields', 'Name', SD_FORMS_FN, SD_FORM_FIELDS_FN)
TABLE_DESIGN = _get_details('Table', 'Fields', 'Name', SD_TABLES_FN, SD_TABLE_FIELDS_FN)
META_FORMS = pd.read_pickle(SD_META_FORMS_FN)

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

##################################################################################################################
# Functions for field_design
##################################################################################################################

FD_COLS = ['Model', 'Field', 'FormRow', 'FormCol', 'FormSection', 'FormLabel', 'FormType', 'FormColumnsSize', 'ViewHeading', 'ViewType', 'ViewArgs', 'ViewHref']
FD_MDL, FD_FLD, FD_ROW, FD_COL, FD_SCT, FD_LBL, FD_TYP, FD_FCS, FD_VHD, FD_VTP, FD_VAR, FD_VHR = FD_COLS


FD_POS = [FD_ROW, FD_COL]
FD_FSV = [FD_SCT, FD_FLD, FD_LBL, FD_FCS]


FD_POS = [FD_ROW, FD_COL]
FD_FSV = [FD_SCT, FD_FLD, FD_LBL, FD_FCS]

def GET_FD(model):
    df = (
        pd.read_pickle(FIELD_DESIGN_FN)
        .query(f'{FD_MDL} == "{model}"')
        .loc[:, FD_FLD:]
    )
    fields = df[FD_FLD].values
    view_headings = df.query(f'{FD_VHD} != ""')[FD_VHD].values
    view_fields = df.query(f'{FD_VHD} != ""')[[FD_VTP, FD_VAR, FD_VHR]].values

    df = (
        df.query(f'{FD_ROW} >= 0')
        .sort_values(FD_POS)
        .reset_index(drop=True)
    )
    if df.shape[0] == 0:
        form_fields, form_type, form_struct = [],[],[]
    else:
        form_fields = df[FD_FLD].values.tolist()
        form_type = df.query(f'{FD_TYP} != ""')[[FD_FLD, FD_TYP]].values
        idxs = df.query(f'{FD_COL} == 0').index
        form_struct = [df[a:b][FD_FSV].values.tolist() for a, b in zip(idxs[:-1], idxs[1:])] + [df[idxs[-1]:][FD_FSV].values.tolist()]

    return fields, form_fields, form_type, form_struct, view_headings, view_fields

##################################################################################################################
# Convenience functions for views.py
##################################################################################################################

def _tmpl(s):
    return loader.get_template(f'home/{s}.html')

def _http(t=None, s=None, c=None, r=None):
    t = _tmpl(s) if t is None else t
    if c is None:
        return HttpResponse(t.render())
    return HttpResponse(t.render(c, r))

##################################################################################################################
# Sidebar List
##################################################################################################################

SIDEBAR = [({'Menu': 'Home', 'MenuId': 'HomePages', 'Icon': 'fas fa-couch'}, [({'SubMenu': 'Dashboard', 'SubId': 'HomeDashboardPages', 'Type': '0', 'Text': 'Dashboard', 'Mini': 'D', 'SubMini': 'H'}, [{'Text': 'Dashboard', 'Mini': 'D', 'HREF': 'Dashboard'}]), ({'SubMenu': 'Profile', 'SubId': 'HomeProfilePages', 'Type': '0', 'Text': 'Profile', 'Mini': 'P', 'SubMini': 'H'}, [{'Text': 'Profile', 'Mini': 'P', 'HREF': 'MyProfile'}]), ({'SubMenu': 'TimeClock', 'SubId': 'HomeTimeClockPages', 'Type': '0', 'Text': 'TimeClock', 'Mini': 'T', 'SubMini': 'H'}, [{'Text': 'TimeClock', 'Mini': 'T', 'HREF': ''}]), ({'SubMenu': 'Calendar', 'SubId': 'HomeCalendarPages', 'Type': '0', 'Text': 'Calendar', 'Mini': 'C', 'SubMini': 'H'}, [{'Text': 'Calendar', 'Mini': 'C', 'HREF': ''}]), ({'SubMenu': 'Events', 'SubId': 'HomeEventsPages', 'Type': '1', 'Text': 'New Event', 'Mini': 'N', 'SubMini': 'H'}, [{'Text': 'New Event', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Events', 'Mini': 'V', 'HREF': ''}])]), ({'Menu': 'Operations', 'MenuId': 'OperationsPages', 'Icon': 'fas fa-business-time'}, [({'SubMenu': 'Inventory', 'SubId': 'OperationsInventoryPages', 'Type': '1', 'Text': 'New Inventory', 'Mini': 'N', 'SubMini': 'O'}, [{'Text': 'New Inventory', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Inventory', 'Mini': 'V', 'HREF': ''}]), ({'SubMenu': 'Orders', 'SubId': 'OperationsOrdersPages', 'Type': '1', 'Text': 'New Order', 'Mini': 'N', 'SubMini': 'O'}, [{'Text': 'New Order', 'Mini': 'N', 'HREF': 'AddOrder'}, {'Text': 'View Orders', 'Mini': 'V', 'HREF': 'ViewOrders'}]), ({'SubMenu': 'DropOff', 'SubId': 'OperationsDropOffPages', 'Type': '1', 'Text': 'New DropOff', 'Mini': 'N', 'SubMini': 'O'}, [{'Text': 'New DropOff', 'Mini': 'N', 'HREF': 'AddDropoff'}, {'Text': 'View DropOffs', 'Mini': 'V', 'HREF': 'ViewDropoffs'}]), ({'SubMenu': 'Items', 'SubId': 'OperationsItemsPages', 'Type': '1', 'Text': 'New Item', 'Mini': 'N', 'SubMini': 'O'}, [{'Text': 'New Item', 'Mini': 'N', 'HREF': 'AddItem'}, {'Text': 'View Items', 'Mini': 'V', 'HREF': 'ViewItems'}])]), ({'Menu': 'Management', 'MenuId': 'ManagementPages', 'Icon': 'fas fa-chess'}, [({'SubMenu': 'Employees', 'SubId': 'ManagementEmployeesPages', 'Type': '1', 'Text': 'New Employee', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Employee', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Employees', 'Mini': 'V', 'HREF': ''}]), ({'SubMenu': 'Consignors', 'SubId': 'ManagementConsignorsPages', 'Type': '1', 'Text': 'New Consignor', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Consignor', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Consignors', 'Mini': 'V', 'HREF': ''}]), ({'SubMenu': 'Liquidators', 'SubId': 'ManagementLiquidatorsPages', 'Type': '1', 'Text': 'New Liquidator', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Liquidator', 'Mini': 'N', 'HREF': 'AddLiquidator'}, {'Text': 'View Liquidators', 'Mini': 'V', 'HREF': 'ViewLiquidators'}]), ({'SubMenu': 'Schedule', 'SubId': 'ManagementSchedulePages', 'Type': '1', 'Text': 'New Schedule', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Schedule', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Schedules', 'Mini': 'V', 'HREF': ''}]), ({'SubMenu': 'Vacation', 'SubId': 'ManagementVacationPages', 'Type': '1', 'Text': 'New Vacation', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Vacation', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Vacation', 'Mini': 'V', 'HREF': ''}]), ({'SubMenu': 'Drawers', 'SubId': 'ManagementDrawersPages', 'Type': '1', 'Text': 'New Drawer', 'Mini': 'N', 'SubMini': 'M'}, [{'Text': 'New Drawer', 'Mini': 'N', 'HREF': ''}, {'Text': 'View Drawers', 'Mini': 'V', 'HREF': ''}])]), ({'Menu': 'Database', 'MenuId': 'DatabasePages', 'Icon': 'fas fa-database'}, [({'SubMenu': 'Stores', 'SubId': 'DatabaseStoresPages', 'Type': '1', 'Text': 'New Store', 'Mini': 'N', 'SubMini': 'D'}, [{'Text': 'New Store', 'Mini': 'N', 'HREF': 'AddStore'}, {'Text': 'View Stores', 'Mini': 'V', 'HREF': 'ViewStores'}]), ({'SubMenu': 'Departments', 'SubId': 'DatabaseDepartmentsPages', 'Type': '1', 'Text': 'New Department', 'Mini': 'N', 'SubMini': 'D'}, [{'Text': 'New Department', 'Mini': 'N', 'HREF': 'AddDepartment'}, {'Text': 'View Departments', 'Mini': 'V', 'HREF': 'ViewDepartments'}]), ({'SubMenu': 'Positions', 'SubId': 'DatabasePositionsPages', 'Type': '1', 'Text': 'New Position', 'Mini': 'N', 'SubMini': 'D'}, [{'Text': 'New Position', 'Mini': 'N', 'HREF': 'AddPosition'}, {'Text': 'View Positions', 'Mini': 'V', 'HREF': 'ViewPositions'}]), ({'SubMenu': 'Sections', 'SubId': 'DatabaseSectionsPages', 'Type': '1', 'Text': 'New Section', 'Mini': 'N', 'SubMini': 'D'}, [{'Text': 'New Section', 'Mini': 'N', 'HREF': 'AddSection'}, {'Text': 'View Sections', 'Mini': 'V', 'HREF': 'ViewSections'}]), ({'SubMenu': 'Locations', 'SubId': 'DatabaseLocationsPages', 'Type': '1', 'Text': 'New Location', 'Mini': 'N', 'SubMini': 'D'}, [{'Text': 'New Location', 'Mini': 'N', 'HREF': 'AddLocation'}, {'Text': 'View Locations', 'Mini': 'V', 'HREF': 'ViewLocations'}])])]