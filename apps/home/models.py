from re import M
from uuid import uuid4
from django.db import models
import os
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal
from django.utils.deconstruct import deconstructible
from .variables import DEPARTMENT_LIST, ORDER_CATEGORY_LIST, EMAIL_PREFERENCES_LIST
from phone_field import PhoneField

##################################################################################################################
# Field Design
##################################################################################################################

# 0-Model       1-Field              2-FormRow  3-FormCol  4-FormSection        5-FormLabel        6-FormType    7-FormColumnsSize  8-ViewHeading     9-ViewVariable     10-ViewHref  
_m = 0
_f = 1
_r = 2
_c = 3
_s = 4
_l = 5
_t = 6
_cs = 7
_h = 8
_v = 9
_a = 10

form_design = [
# 0-Model       1-Field               2-FormRow  3-FormCol  4-FormSection        5-FormLabel         6-FormType    7-FormColumnsSize  8-ViewHeading       9-ViewVariable           10-ViewHref                           
[ 'Consignor',  'user',               None,      None,      None,                None,               None,         None,              'User',             'user_id',               'management-consignor-edit.html?pk='   ],
[ 'Consignor',  'address',            0,         0,         None,                'Address',          None,         6,                 'Address',          'address',               None                                   ],
[ 'Consignor',  'address2',           0,         1,         None,                'Address2',         'date',       6,                 'Address2',         'address2',              None                                   ],
[ 'Consignor',  'city',               1,         0,         None,                'City',             None,         4,                 'City',             'city',                  None                                   ],
[ 'Consignor',  'state',              1,         1,         None,                'State',            None,         4,                 'State',            'state',                 None                                   ],
[ 'Consignor',  'zip',                1,         2,         None,                'Zip',              None,         4,                 'Zip',              'zip',                   None                                   ],
[ 'Consignor',  'phone',              2,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'phone',                 None                                   ],
[ 'Consignor',  'waiver_date',        3,         0,         None,                'WaiverDate',       'date',       6,                 'WaiverDate',       'waiver_date',           None                                   ],
[ 'Consignor',  'waiver_image',       4,         0,         None,                'Waiver',           'img1',       12,                'Waiver',           'waiver_image',          None                                   ],
[ 'Consignor',  'image',              5,         0,         None,                'Image',            'img1',       12,                'Image',            'image',                 None                                   ],
[ 'Consignor',  'pid_type',           6,         0,         None,                'PIDType',          None,         6,                 'PIDType',          'pid_type',              None                                   ],
[ 'Consignor',  'pid_image',          7,         0,         None,                'PID',              'img1',       12,                'PID',              'pid_image',             None                                   ],
[ 'Employee',   'user',               None,      None,      None,                None,               None,         None,              'User',             'user_id',               'management-employee-edit.html?pk='    ],
[ 'Employee',   'title',              0,         0,         'EmployeeDetails',   'Title',            None,         6,                 'Title',            'title',                 None                                   ],
[ 'Employee',   'hourly_rate',        0,         1,         None,                'HourlyRate',       None,         6,                 'HourlyRate',       'hourly_rate',           None                                   ],
[ 'Employee',   'address',            1,         0,         None,                'Address',          None,         6,                 'Address',          'address',               None                                   ],
[ 'Employee',   'address2',           1,         1,         None,                'Address2',         None,         6,                 'Address2',         'address2',              None                                   ],
[ 'Employee',   'city',               2,         0,         None,                'City',             None,         4,                 'City',             'city',                  None                                   ],
[ 'Employee',   'state',              2,         1,         None,                'State',            None,         4,                 'State',            'state',                 None                                   ],
[ 'Employee',   'zip',                2,         2,         None,                'Zip',              None,         4,                 'Zip',              'zip',                   None                                   ],
[ 'Employee',   'phone',              3,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'phone',                 None                                   ],
[ 'Employee',   'date_of_birth',      3,         1,         None,                'DateOfBirth',      'date',       6,                 'DateOfBirth',      'date_of_birth',         None                                   ],
[ 'Employee',   'ice1_fname',         4,         0,         'EmergencyContact1', 'FirstName',        None,         6,                 'FirstName',        'ice1_fname',            None                                   ],
[ 'Employee',   'ice1_lname',         4,         1,         None,                'LastName',         None,         6,                 'LastName',         'ice1_lname',            None                                   ],
[ 'Employee',   'ice1_phone',         5,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'ice1_phone',            None                                   ],
[ 'Employee',   'ice1_relationship',  5,         1,         None,                'Relationship',     None,         6,                 'Relationship',     'ice1_relationship',     None                                   ],
[ 'Employee',   'ice2_fname',         6,         0,         'EmergencyContact2', 'FirstName',        None,         6,                 'FirstName',        'ice2_fname',            None                                   ],
[ 'Employee',   'ice2_lname',         6,         1,         None,                'LastName',         None,         6,                 'LastName',         'ice2_lname',            None                                   ],
[ 'Employee',   'ice2_phone',         7,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'ice2_phone',            None                                   ],
[ 'Employee',   'ice2_relationship',  7,         1,         None,                'Relationship',     None,         6,                 'Relationship',     'ice2_relationship',     None                                   ],
[ 'Employee',   'start_date',         8,         0,         None,                'StartDate',        'date',       6,                 'StartDate',        'start_date',            None                                   ],
[ 'Employee',   'end_date',           8,         1,         None,                'EndDate',          'date',       6,                 'EndDate',          'end_date',              None                                   ],
[ 'Employee',   'exit_reason',        9,         0,         None,                'ExitReason',       None,         12,                'ExitReason',       'exit_reason',           None                                   ],
[ 'Employee',   'image',              10,        0,         None,                'Image',            'img1',       12,                'Image',            'image',                 None                                   ],
[ 'Liquidator', 'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'management-liquidator-edit.html?pk='  ],
[ 'Liquidator', 'name',               0,         0,         None,                'Name',             None,         6,                 'Name',             'name',                  None                                   ],
[ 'Liquidator', 'description',        0,         1,         None,                'Description',      None,         6,                 'Description',      'description',           None                                   ],
[ 'Liquidator', 'website',            1,         0,         None,                'Website',          None,         12,                'Website',          'website',               None                                   ],
[ 'Liquidator', 'contact_phone',      2,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'contact_phone',         None                                   ],
[ 'Liquidator', 'contact_email',      2,         1,         None,                'Email',            None,         6,                 'Email',            'contact_email',         None                                   ],
[ 'Order',      'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'operations-order-edit.html?pk='       ],
[ 'Order',      'order_number',       0,         0,         'OrderDetails',      'OrderNumber',      None,         6,                 'OrderNumber',      'order_number',          None                                   ],
[ 'Order',      'purchase_date',      0,         1,         None,                'PurchaseDate',     'date',       6,                 'PurchaseDate',     'purchase_date',         None                                   ],
[ 'Order',      'liquidator',         1,         0,         None,                'Liquidator',       None,         6,                 'Liquidator',       'liquidator_id',         'management-liquidator-edit.html?pk='  ],
[ 'Order',      'category',           1,         1,         None,                'Category',         None,         6,                 'Category',         'category',              None                                   ],
[ 'Order',      'item_count',         2,         0,         None,                'ItemCount',        None,         6,                 'Items',            'item_count',            None                                   ],
[ 'Order',      'pallet_count',       2,         1,         None,                'PalletCount',      None,         6,                 'Pallets',          'pallet_count',          None                                   ],
[ 'Order',      'sale_amount',        3,         0,         None,                'SaleAmount',       None,         6,                 'SaleAmount',       'sale_amount',           None                                   ],
[ 'Order',      'shipping_amount',    3,         1,         None,                'ShippingAmount',   None,         6,                 'ShippingAmount',   'shipping_amount',       None                                   ],
[ 'Order',      'delivery_date',      4,         0,         'DeliveryDetails',   'DeliveryDate',     'date',       6,                 'DeliveryDate',     'delivery_date',         None                                   ],
[ 'Order',      'accepted_by',        5,         0,         None,                'AcceptedBy',       None,         6,                 None,               'accepted_by_id',        None                                   ],
[ 'Order',      'unloaded_by',        5,         1,         None,                'UnloadedBy',       None,         6,                 None,               'unloaded_by_id',        None                                   ],
[ 'Order',      'pod_image',          6,         0,         None,                'ProofofDelivery',  'img1',       12,                'POD',              'pod_image',             None                                   ],
[ 'Order',      'manifest_file',      7,         0,         None,                'ManifestFile',     'file',       6,                 'Manifest',         'manifest_file',         None                                   ],
[ 'Shopper',    'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    None                                   ],
[ 'Shopper',    'user',               None,      None,      None,                None,               None,         None,              'User',             'user_id',               None                                   ],
[ 'Shopper',    'email_preferences',  0,         0,         None,                'EmailPreferences', None,         6,                 'EmailPreferences', 'email_preferences',     None                                   ],
[ 'Shopper',    'waiver_date',        1,         0,         None,                'WaiverDate',       'date',       6,                 'WaiverDate',       'waiver_date',           None                                   ],
[ 'Shopper',    'waiver_image',       2,         0,         None,                'Waiver',           'img1',       12,                'Waiver',           'waiver_image',          None                                   ],
[ 'Store',      'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'database-store-edit.html?pk='         ],
[ 'Store',      'name',               0,         0,         None,                'Name',             None,         6,                 'Name',             'name',                  None                                   ],
[ 'Store',      'general_manager',    0,         1,         None,                'GeneralManager',   None,         6,                 'GeneralManager',   'general_manager_id',    None                                   ],
[ 'Store',      'address',            1,         0,         'Location',          'Address',          None,         6,                 'Address',          'address',               None                                   ],
[ 'Store',      'address2',           1,         1,         None,                'Address2',         None,         6,                 'Address2',         'address2',              None                                   ],
[ 'Store',      'city',               2,         0,         None,                'City',             None,         4,                 'City',             'city',                  None                                   ],
[ 'Store',      'state',              2,         1,         None,                'State',            None,         4,                 'State',            'state',                 None                                   ],
[ 'Store',      'zip',                2,         2,         None,                'Zip',              None,         4,                 'Zip',              'zip',                   None                                   ],
[ 'Store',      'phone',              3,         0,         None,                'Phone',            'tel',        6,                 'Phone',            'phone',                 None                                   ],
[ 'Store',      'email',              3,         1,         None,                'Email',            None,         6,                 'Email',            'email',                 None                                   ],
[ 'User',       'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    None                                   ],
[ 'User',       'first_name',         0,         0,         None,                'FirstName',        None,         6,                 'FirstName',        'first_name',            None                                   ],
[ 'User',       'last_name',          0,         1,         None,                'LastName',         None,         6,                 'LastName',         'last_name',             None                                   ],
[ 'User',       'email',              1,         0,         None,                'Email',            None,         12,                'Email',            'email',                 None                                   ],
[ 'User',       'is_active',          None,      None,      None,                None,               None,         None,              'Active',           'is_active',             None                                   ],
[ 'User',       'date_joined',        None,      None,      None,                None,               None,         None,              'DateJoined',       'date_joined',           None                                   ],
[ 'User',       'last_login',         None,      None,      None,                None,               None,         None,              'LastLogin',        'last_login',            None                                   ],
[ 'User',       'password',           None,      None,      None,                None,               None,         None,              None,               None,                    None                                   ],
[ 'User',       'is_staff',           None,      None,      None,                None,               None,         None,              'Staff',            'is_staff',              None                                   ],
[ 'User',       'is_superuser',       None,      None,      None,                None,               None,         None,              'Superuser',        'is_superuser',          None                                   ],
[ 'User',       'username',           None,      None,      None,                None,               None,         None,              'Username',         'username',              None                                   ],
[ 'Dropoff',    'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'operations-dropoff-edit.html?pk='     ],
[ 'Dropoff',    'employee',           0,         0,         None,                'Employee',         None,         4,                 'Employee',         'employee_id',           None                                   ],
[ 'Dropoff',    'consignor',          0,         1,         None,                'Consignor',        None,         4,                 'Consignor',        'consignor_id',          None                                   ],
[ 'Dropoff',    'date',               0,         2,         None,                'Date',             'date',       4,                 'Date',             'date',                  None                                   ],
[ 'Dropoff',    'comments',           1,         0,         None,                'Comments',         None,         12,                'Comments',         'comments',              None                                   ],
[ 'Dropoff',    'agreement_image',    2,         0,         None,                'Agreement',        'img1',       12,                'Agreement',        'agreement_image',       None                                   ],
[ 'Dropoff',    'offer_amount',       3,         0,         None,                'OfferAmount',      None,         6,                 'OfferAmount',      'offer_amount',          None                                   ],
[ 'Department', 'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'database-department-edit.html?pk='    ],
[ 'Department', 'store',              0,         0,         None,                'Store',            None,         6,                 'Store',            'store_id',              None                                   ],
[ 'Department', 'name',               0,         1,         None,                'Name',             None,         6,                 'Name',             'name',                  None                                   ],
[ 'Department', 'department_manager', 1,         0,         None,                'ManagedBy',        None,         6,                 'ManagedBy',        'department_manager_id', None                                   ],
[ 'Position',   'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'database-position-edit.html?pk='      ],
[ 'Position',   'department',         0,         0,         None,                'Department',       None,         6,                 'Department',       'department_id',         None                                   ],
[ 'Position',   'name',               0,         1,         None,                'Name',             None,         6,                 'Name',             'name',                  None                                   ],
[ 'Section',    'id',                 None,      None,      None,                None,               None,         None,              'ID',               'id',                    'database-section-edit.html?pk='       ],
[ 'Section',    'department',         0,         0,         None,                'Department',       None,         6,                 'Department',       'department_id',         None                                   ],
[ 'Section',    'name',               0,         1,         None,                'Name',             None,         6,                 'Name',             'name',                  None                                   ]
]

# This function helps get the form structure from the row columns in field_design
def structure_from_list(fd):
    struct = []
    row, r, c = [], 0, -1
    for l in fd:
        if l[_r] > r:
            struct += [row]
            row = []
        section, field, label, colsize = l[_s], l[_f], l[_l], l[_cs]
        row += [(section, field, label, colsize)]
        r, c = l[_r], l[_c]
    struct += [row]
    return struct

# Processes the field design into iterables for templates, forms etc
def process_field_design(model):
    fd = [ f for f in form_design if f[_m] == model]
    fields = [f[_f] for f in fd]
    form_fields = [f[_f] for f in fd if f[_r] is not None]
    form_type = [(f[_f], f[_t]) for f in fd if f[_t]]
    form_struct = structure_from_list([f for f in fd if f[_r] is not None])
    view_headings = [(f[_h]) for f in fd if f[_h]] 
    view_fields = [(f[_v], f[_a]) for f in fd if f[_h]]
    return fields, form_fields, form_type, form_struct, view_headings, view_fields
    

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
employee_image = PathAndRename("user-employee-image")
shopper_waiver = PathAndRename("user-shopper-waiver")
consignor_waiver = PathAndRename("user-consignor-waiver")
consignor_image = PathAndRename("user-consignor-image")
consignor_pid = PathAndRename("user-consignor-pid")
order_image = PathAndRename("order-image")
order_manifest = PathAndRename("order-manifest")
order_pod = PathAndRename("order-pod")
dropoff_agreement = PathAndRename("dropoff-agreement")

##################################################################################################################
# Model Classes
##################################################################################################################

class BasicUser(User):
    
    model_name = 'User'
    form_name = 'Basic Information'
    pk = 'user_id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)

@receiver(post_save, sender=User)
def create_user_extentions(sender, instance, created, **kwargs):
    if created:
        Employee.objects.create(user=instance)
        Shopper.objects.create(user=instance)
        Consignor.objects.create(user=instance)

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)    
    address = models.CharField(max_length=100, blank=True, default='')
    address2 = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=30, blank=True, default='')
    state = models.CharField(max_length=30, blank=True, default='')
    zip = models.CharField(max_length=5, blank=True, default='')
    phone = PhoneField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True, default=None)
    ice1_fname = models.CharField(max_length=30, blank=True, default='')
    ice1_lname = models.CharField(max_length=30, blank=True, default='')
    ice1_phone = PhoneField(blank=True)
    ice1_relationship = models.CharField(max_length=30, blank=True, default='')
    ice2_fname = models.CharField(max_length=30, blank=True, default='')
    ice2_lname = models.CharField(max_length=30, blank=True, default='')
    ice2_phone = PhoneField(blank=True)
    ice2_relationship = models.CharField(max_length=30, blank=True, default='')
    exit_reason = models.CharField(max_length=30, blank=True, default='')
    start_date = models.DateField(null=True, blank=True, default=None)
    end_date = models.DateField(null=True, blank=True, default=None)
    title = models.CharField(max_length=30, blank=True, default='')
    hourly_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, default=Decimal(0) )
    image = models.ImageField(upload_to=employee_image, default='', blank=True)

    model_name = 'Employee'
    form_name = 'Employee Information'
    pk = 'user_id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)

    def __str__(self):        
        return f'{self.title} - {self.user.first_name} {self.user.last_name}'

class Shopper(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    waiver_image = models.ImageField(upload_to=shopper_waiver, default='', blank=True)
    waiver_date = models.DateField(null=True, blank=True, default=None)
    email_preferences = models.CharField(max_length=30, choices=EMAIL_PREFERENCES_LIST, default='', blank=True)

    model_name = 'Shopper'
    form_name = 'Shopper Information'
    pk = 'user_id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)

    def __str__(self):
        return f'Shopper - {self.user.first_name} {self.user.last_name}'

class Consignor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100, blank=True, default='')
    address2 = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=30, blank=True, default='')
    state = models.CharField(max_length=30, blank=True, default='')
    zip = models.CharField(max_length=5, blank=True, default='')
    phone = PhoneField(blank=True)
    waiver_image = models.ImageField(upload_to=consignor_waiver, default='', blank=True)
    waiver_date = models.DateField(null=True, blank=True, default=None)
    image = models.ImageField(upload_to=consignor_image, default='', blank=True)
    pid_type = models.CharField(max_length=30, blank=True, default='')
    pid_image = models.ImageField(upload_to=consignor_pid, default='', blank=True)

    model_name = 'Consignor'
    form_name = 'Consignor Information'
    pk = 'user_id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):        
        return f'Consignor - {self.user.first_name} {self.user.last_name}'

class Liquidator(models.Model):
    name = models.CharField(max_length=30, blank=True, default='')
    description = models.CharField(max_length=50, blank=True, default='')
    website = models.CharField(max_length=30, blank=True, default='')
    contact_phone = PhoneField(blank=True)
    contact_email = models.CharField(max_length=50, blank=True, default='')

    model_name = 'Liquidator'
    form_name = 'Liquidator Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        return f'Liquidator - {self.name}'

class Order(models.Model):
    liquidator = models.ForeignKey(Liquidator, on_delete=models.SET_NULL, null=True)
    accepted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='accepted_orders', null=True)
    unloaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='unloaded_orders', null=True)
    order_number = models.CharField(max_length=30, blank=True, default='')
    category = models.CharField(max_length=30, choices=ORDER_CATEGORY_LIST)
    item_count = models.IntegerField(blank=False, default=0)
    pallet_count = models.IntegerField(blank=False, default=0)
    sale_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=Decimal(0) )
    shipping_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=Decimal(0) )
    purchase_date = models.DateField(null=True, blank=True, default=None)
    delivery_date = models.DateField(null=True, blank=True, default=None)
    pod_image = models.ImageField(upload_to=order_pod, default='', blank=True)
    manifest_file = models.FileField(upload_to=order_manifest, default='', blank=True)
    
    model_name = 'Order'
    form_name = 'Order Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self) -> str:
        return f'ORDER {self.id}'

class Dropoff(models.Model):
    consignor = models.ForeignKey(Consignor, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    date = models.DateField(null=True, blank=True, default=None)
    comments = models.CharField(max_length=1000, blank=True, default='')
    agreement_image = models.ImageField(upload_to=dropoff_agreement, default='', blank=True)
    offer_amount = models.DecimalField(max_digits=8, decimal_places=2, blank=False, default=Decimal(0) )
    
    model_name = 'Dropoff'
    form_name = 'Dropoff Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        return f'Dropoff {self.id}'

class OrderImages(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=order_image, default='', blank=True)

class Store(models.Model):
    general_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='managed_stores', null=True)
    name = models.CharField(max_length=30, blank=True, default='')
    address = models.CharField(max_length=100, blank=True, default='')
    address2 = models.CharField(max_length=100, blank=True, default='')
    city = models.CharField(max_length=30, blank=True, default='')
    state = models.CharField(max_length=30, blank=True, default='')
    zip = models.CharField(max_length=5, blank=True, default='')
    phone = PhoneField(blank=True)
    email = models.CharField(max_length=50, blank=True, default='')

    model_name = 'Store'
    form_name = 'Store Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        if self.general_manager is None:
            return f'{self.name}'
        else:
            return f'{self.name} - Manager({self.general_manager.user.first_name} {self.general_manager.user.last_name})'

class Department(models.Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, null=True)
    department_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, related_name='managed_departments', null=True)
    name = models.CharField(max_length=30, choices=DEPARTMENT_LIST)

    model_name = 'Department'
    form_name = 'Department Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        s = (
                f'{self.store.name}-' if self.store else ''
            ) + self.name
        if self.department_manager: 
            s += f' - Manager({self.department_manager.user.first_name} {self.department_manager.user.last_name})'
        return s

class Position(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)

    model_name = 'Position'
    form_name = 'Position Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        return f'{self.department.name}-{self.name}' if self.department else f'{self.name}'

class Section(models.Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=30)

    model_name = 'Section'
    form_name = 'Section Information'
    pk = 'id'

    # The following is used by the forms and the templates
    fields, form_fields, form_type, form_struct, view_headings, view_fields = process_field_design(model_name)
    
    def __str__(self):
        return f'Dept:{self.department.name} Sect:{self.name}' if self.department else f'Sect:{self.name}'