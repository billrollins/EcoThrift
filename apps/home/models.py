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
    base_user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    def __str__(self):
        return f'{STR_FULL_NM(self.base_user)} ({self.base_user.username})'

class Shopper(Model):
    user = models.OneToOneField(ExtendedUser, on_delete=models.CASCADE, primary_key=True)
    waiver_image = models.ImageField(blank=True, default='', null=False, upload_to=SHP_WAV)
    waiver_date = models.DateField(blank=True, default=None, null=True)
    email_preferences = models.CharField(max_length=50, blank=True, default='', null=False, choices=EMAIL_PREFERENCES_LIST)
    def __str__(self):
        return f'{self.user}'

class Consignor(Model):
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
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    website = models.CharField(max_length=100, blank=True, default='', null=False)
    contact_phone = PhoneNumberField(blank=True, region='US')
    contact_email = models.CharField(max_length=100, blank=True, default='', null=False)
    def __str__(self):
        return f'{self.name}'

class Store(Model):
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
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    department_manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    def __str__(self):
        return f'({self.store.name}) {self.name}|{STR_FULL_NM(self.department_manager.user.base_user) if self.department_manager else ""}'

class Section(Model):
    store = models.ForeignKey(Store, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    def __str__(self):
        return f'({self.store.name if self.store else ""}) {self.name}'

class Location(Model):
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    label = models.CharField(max_length=5, blank=True, default='', null=False)
    def __str__(self):
        return f'{self.section if self.section else ""} : {self.label}'

class Position(Model):
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    name = models.CharField(max_length=30, blank=True, default='', null=False)
    def __str__(self):
        return f'({self.department.name if self.department else ""}) {self.name}'

class Dropoff(Model):
    consignor = models.ForeignKey(Consignor, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=False, default=None, null=True)
    date = models.DateField(blank=True, default=date.today, null=False)
    comments = models.CharField(max_length=100, blank=True, default='', null=False)
    agreement_image = models.ImageField(blank=True, default='', null=False, upload_to=DRP_AGR)
    offer_amount = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    def __str__(self):
        return f'(Drop {self.id}) {self.employee}|{self.comments[:50]}'

class Order(Model):
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

class Item(Model):
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    dropoff = models.ForeignKey(Dropoff, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    created_date = models.DateField(blank=True, default=date.today, null=False)
    description = models.CharField(max_length=100, blank=True, default='', null=False)
    brand = models.CharField(max_length=100, blank=True, default='', null=False)
    condition = models.CharField(max_length=50, blank=True, default='', null=False, choices=CONDITION_LIST)
    model = models.CharField(max_length=100, blank=True, default='', null=False)
    retail_amount = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2)
    department = models.CharField(max_length=100, blank=True, default='', null=False)
    item_class = models.CharField(max_length=100, blank=True, default='', null=False)
    category = models.CharField(max_length=100, blank=True, default='', null=False)
    subcategory = models.CharField(max_length=100, blank=True, default='', null=False)
    image = models.ImageField(blank=True, default='', null=False, upload_to=ITM_IMG)
    price_code = models.CharField(max_length=2, blank=True, default='', null=False)
    static_price = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2, choices=PRICE_LIST)
    expected_price = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2, choices=PRICE_LIST)
    starting_price = models.DecimalField(blank=True, default=None, null=True, max_digits=8, decimal_places=2, choices=PRICE_LIST)
    status = models.CharField(max_length=50, blank=True, default='', null=False, choices=STATUS_CHANGE_LIST)
    tested = models.CharField(max_length=50, blank=True, default='', null=False, choices=TESTED_LIST)
    zero_date = models.DateField(blank=True, default=None, null=True)
    status_date = models.DateField(blank=True, default=None, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, blank=True, default=None, null=True)
    tags = models.CharField(max_length=999, blank=True, default='', null=False)
    def __str__(self):
        return f'{self.id} {self.location}|{self.description[:50]}'	

#############################################################
# Paste Model Code Above this line
#############################################################	

def MODELS(class_name):
    return globals()[class_name]

##################################################################################################################
# DB Choice Lists
##################################################################################################################


STORE_CHOICES = [(o.pk, o.name) for o in Store.objects.all()]
SECTION_CHOICES = [(o.pk, o.name) for o in Section.objects.all()]

LOCATION_CHOICES = [(o.pk, o.label) for o in Location.objects.all()]

DEPARTMENT_CHOICES = [(o.pk, o.name) for o in Department.objects.all()]
POSITION_CHOICES = [(o.pk, o.name) for o in Position.objects.all()]

ORDER_CHOICES = [(o.pk, f'#{o.order_number}') for o in Order.objects.all()]
DROPOFF_CHOICES = [(o.pk, f'{o.id}|{o.comments[:50]}') for o in Dropoff.objects.all()]










