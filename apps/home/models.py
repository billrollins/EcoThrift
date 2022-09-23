from .variables import *

#############################################################
#Rebase Database: in git bash ->
#
# python manage.py makemigrations
# python manage.py migrate --fake home zero
# find . -path '*/home/migrations/*.py' -not -name '__init__.py' -delete
# find . -path '*apps/*__pycache__/*' -delete
# find . -path '*apps/*__pycache__' -delete
# python manage.py makemigrations
# python manage.py migrate --fake-initial
# python manage.py showmigrations

#############################################################

#############################################################
# Paste Model Code Below this line
#############################################################	

class ExtendedUser(Model):
    model_name, _pk_ = 'ExtendedUser', 'base_user_id'
    model_design = MODEL_DESIGN[model_name]
    
    base_user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    def __str__(self):
        return f'{STR_FULL_NM(self.base_user)} ({self.base_user.username})'

class Shopper(Model):
    model_name, _pk_ = 'Shopper', 'user_id'
    model_design = MODEL_DESIGN[model_name]
    
    user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, primary_key=True)
    waiver_image = models.ImageField(blank=True, default='', null=False, upload_to=SHP_WAV)
    waiver_date = models.DateField(blank=True, default=None, null=True)
    email_preferences = models.CharField(max_length=50, blank=True, default='', null=False, choices=EMAIL_PREFERENCES_LIST)
    
    def __str__(self):
        return f'{self.user}'

class Consignor(Model):
    model_name, _pk_ = 'Consignor', 'user_id'
    model_design = MODEL_DESIGN[model_name]
    
    user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100, blank=True, default='', null=False)
    address2 = models.CharField(max_length=100, blank=True, default='', null=False)
    city = models.CharField(max_length=30, blank=True, default='', null=False)
    state = models.CharField(max_length=2, blank=True, default='', null=False, choices=ST_LIST)
    zip = models.CharField(max_length=5, blank=True, default='', null=False)
    phone = PhoneNumberField(blank=True, region='US')
    waiver_image = models.ImageField(blank=True, default='', null=False, upload_to=CON_WAV)
    waiver_date = models.DateField(blank=True, default=None, null=True)
    image = models.ImageField(blank=True, default='', null=False, upload_to=CON_IMG)
    pid_type = models.CharField(max_length=50, blank=True, default='', null=False, choices=PID_LIST)
    pid_image = models.ImageField(blank=True, default='', null=False, upload_to=CON_PID)
    
    def __str__(self):
        return f'{self.user}'

class Employee(Model):
    model_name, _pk_ = 'Employee', 'user_id'
    model_design = MODEL_DESIGN[model_name]
    
    user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, primary_key=True)
    address = models.CharField(max_length=100, blank=True, default='', null=False)
    address2 = models.CharField(max_length=100, blank=True, default='', null=False)
    city = models.CharField(max_length=30, blank=True, default='', null=False)
    state = models.CharField(max_length=2, blank=True, default='', null=False, choices=ST_LIST)
    zip = models.CharField(max_length=5, blank=True, default='', null=False)
    phone = PhoneNumberField(blank=True, region='US')
    date_of_birth = models.DateField(blank=True, default=None, null=True)
    ice1_fname = models.CharField(max_length=30, blank=True, default='', null=False)
    ice1_lname = models.CharField(max_length=30, blank=True, default='', null=False)
    ice1_phone = PhoneNumberField(blank=True, region='US')
    ice1_relationship = models.CharField(max_length=30, blank=True, default='', null=False)
    ice2_fname = models.CharField(max_length=30, blank=True, default='', null=False)
    ice2_lname = models.CharField(max_length=30, blank=True, default='', null=False)
    ice2_phone = PhoneNumberField(blank=True, region='US')
    ice2_relationship = models.CharField(max_length=30, blank=True, default='', null=False)
    exit_reason = models.CharField(max_length=100, blank=True, default='', null=False)
    start_date = models.DateField(blank=True, default=DEFAULT_START_DATE, null=False)
    end_date = models.DateField(blank=True, default=DEFAULT_END_DATE, null=False)
    title = models.CharField(max_length=30, blank=True, default='', null=False)
    hourly_rate = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    image = models.ImageField(blank=True, default='', null=False, upload_to=EMP_IMG)
    
    def __str__(self):
        return f'{self.title}|{self.user}'

class Liquidator(Model):
    model_name, _pk_ = 'Liquidator', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    website = models.CharField(max_length=100, blank=True, default='', null=False)
    contact_phone = PhoneNumberField(blank=True, region='US')
    contact_email = models.CharField(max_length=100, blank=True, default='', null=False)
    
    def __str__(self):
        return f'{self.name}'

class Store(Model):
    model_name, _pk_ = 'Store', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    general_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    address = models.CharField(max_length=100, blank=True, default='', null=False)
    address2 = models.CharField(max_length=100, blank=True, default='', null=False)
    city = models.CharField(max_length=30, blank=True, default='', null=False)
    state = models.CharField(max_length=2, blank=True, default='', null=False, choices=ST_LIST)
    zip = models.CharField(max_length=5, blank=True, default='', null=False)
    phone = PhoneNumberField(blank=True, region='US')
    email = models.CharField(max_length=100, blank=True, default='', null=False)
    
    def __str__(self):
        return f'({STR_LOC_2(self)}) {self.name}|{STR_FULL_NM(self.general_manager.user.base_user) if self.general_manager else ""}'

class Department(Model):
    model_name, _pk_ = 'Department', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    department_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    
    def __str__(self):
        return f'({self.store.name}) {self.name}|{STR_FULL_NM(self.department_manager.user.base_user) if self.department_manager else ""}'

class Section(Model):
    model_name, _pk_ = 'Section', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    
    def __str__(self):
        return f'({self.store.name if self.store else ""}) {self.name}'

class Location(Model):
    model_name, _pk_ = 'Location', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    label = models.CharField(max_length=5, blank=True, default='', null=False)
    
    def __str__(self):
        return f'{self.section if self.section else ""} : {self.label}'

class Position(Model):
    model_name, _pk_ = 'Position', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    
    def __str__(self):
        return f'({self.department.name if self.department else ""}) {self.name}'

class Dropoff(Model):
    model_name, _pk_ = 'Dropoff', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    consignor = models.ForeignKey(Consignor, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    date = models.DateField(blank=True, default=date.today, null=False)
    comments = models.CharField(max_length=100, blank=True, default='', null=False)
    agreement_image = models.ImageField(blank=True, default='', null=False, upload_to=DRP_AGR)
    offer_amount = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f'(Drop {self.id}) {self.employee}|{self.comments[:50]}'

class Order(Model):
    model_name, _pk_ = 'Order', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    liquidator = models.ForeignKey(Liquidator, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    accepted_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, default=None, null=True, related_name='accepted_orders')
    unloaded_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, default=None, null=True, related_name='unloaded_orders')
    order_number = models.CharField(max_length=30, blank=True, default='', null=False)
    category = models.CharField(max_length=100, blank=True, default='', null=False)
    item_count = models.IntegerField(blank=True, default=0, null=False)
    pallet_count = models.IntegerField(blank=True, default=0, null=False)
    sale_amount = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    shipping_amount = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    purchase_date = models.DateField(blank=True, default=date.today, null=False)
    delivery_date = models.DateField(blank=True, default=None, null=True)
    pod_image = models.ImageField(blank=True, default='', null=False, upload_to=ORD_POD)
    manifest_file = models.FileField(blank=True, default=None, null=True, upload_to=ORD_MAN)
    
    def __str__(self):
        return f'#{self.order_number}'

class Order_Images(Model):
    model_name, _pk_ = 'Order_Images', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    image = models.ImageField(blank=True, default='', null=False, upload_to=ORD_IMG)
    
    def __str__(self):
        return f'({self.order.order_number if self.order else ""}) {self.image}'

class Item(Model):
    model_name, _pk_ = 'Item', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    dropoff = models.ForeignKey(Dropoff, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    created_date = models.DateField(blank=True, default=date.today, null=False)
    zero_date = models.DateField(blank=True, default=None, null=True)
    change_date = models.DateField(blank=True, default=None, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    brand = models.CharField(max_length=100, blank=True, default='', null=False)
    condition = models.CharField(max_length=50, blank=True, default='', null=False, choices=CONDITION_LIST)
    tested = models.CharField(max_length=50, blank=True, default='', null=False, choices=TESTED_LIST)
    tags = models.CharField(max_length=999, blank=True, default='', null=False)
    price_code = models.CharField(max_length=2, blank=True, default='', null=False)
    static_price = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    expected_price = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    status_change = models.CharField(max_length=50, blank=True, default='', null=False, choices=STATUS_CHANGE_LIST)
    
    def __str__(self):
        return f'{self.id} {self.location}|{self.description[:50]}'

class Item_Images(Model):
    model_name, _pk_ = 'Item_Images', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    item = models.ForeignKey(Item, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    image = models.ImageField(blank=True, default='', null=False, upload_to=ITM_IMG)
    
    def __str__(self):
        return f'(Item {self.item.id if self.item else ""}) {self.image}'

class Dropoff_Line(Model):
    model_name, _pk_ = 'Dropoff_Line', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    # No Fields Defined
    
    def __str__(self):
        return f'(Drop {self.dropoff.id}) ${self.ext_retail:06.0f} {self.quantity:3}@{self.unit_retail:.2f} "{self.description[:50]}"'

class Order_Line(Model):
    model_name, _pk_ = 'Order_Line', 'id'
    model_design = MODEL_DESIGN[model_name]
    
    # No Fields Defined
    
    def __str__(self):
        return f'({self.order.order_number}) ${self.ext_retail:06.0f} {self.quantity:3}@{self.unit_retail:.2f} "{self.description[:50]}"'

MODELS = {'ExtendedUser':ExtendedUser, 'Shopper':Shopper, 'Consignor':Consignor, 'Employee':Employee, 'Liquidator':Liquidator, 'Store':Store, 'Department':Department, 'Section':Section, 'Location':Location, 'Position':Position, 'Dropoff':Dropoff, 'Order':Order, 'Order_Images':Order_Images, 'Item':Item, 'Item_Images':Item_Images, 'Dropoff_Line':Dropoff_Line, 'Order_Line':Order_Line}	
