from .models import *

class BasicForm(ModelForm):
  __dict__ = {}
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    for form_field in FORM_DESIGN[type(self).__name__]['Fields']:
      widget = self.fields[form_field['Field']].widget
      if form_field['Template']: widget.template_name = form_field['Template']
      if form_field['Class']: widget.attrs['class'] = form_field['Class']
      if form_field['Type']: widget.input_type = form_field['Type']
    self.set_dict()
    return
  def set_dict(self):
    self.__dict__ = self.fields
    self.__dict__.update({'pk':self.instance.pk})
    return



#############################################################
# Paste Form Code Below this line
#############################################################	

class LiquidatorForm(BasicForm):
    class Meta:
      model = Liquidator
      fields = ['name', 'description', 'website', 'contact_phone', 'contact_email']

class StoreForm(BasicForm):
    class Meta:
      model = Store
      fields = ['name', 'general_manager', 'address', 'address2', 'city', 'state', 'zip', 'phone', 'email']

class DepartmentForm(BasicForm):
    class Meta:
      model = Department
      fields = ['store', 'name', 'department_manager']

class SectionForm(BasicForm):
    class Meta:
      model = Section
      fields = ['store', 'name', 'description']

class LocationForm(BasicForm):
    class Meta:
      model = Location
      fields = ['section', 'label']

class PositionForm(BasicForm):
    class Meta:
      model = Position
      fields = ['department', 'name']

class DropoffForm(BasicForm):
    class Meta:
      model = Dropoff
      fields = ['employee', 'consignor', 'date', 'comments', 'agreement_image', 'offer_amount']

class OrderForm(BasicForm):
    class Meta:
      model = Order
      fields = ['order_number', 'purchase_date', 'liquidator', 'category', 'item_count', 'pallet_count', 'sale_amount', 'shipping_amount', 'delivery_date', 'accepted_by', 'unloaded_by', 'pod_image', 'manifest_file']

class ItemForm(BasicForm):
    class Meta:
      model = Item
      fields = ['employee', 'order', 'dropoff', 'created_date', 'zero_date', 'change_date', 'section', 'description', 'brand', 'condition', 'tested', 'tags', 'price_code', 'static_price', 'expected_price', 'status_change']

class UserForm(BasicForm):
    class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email']

class ShopperForm(BasicForm):
    class Meta:
      model = Shopper
      fields = ['waiver_date', 'waiver_image', 'email_preferences']

class ConsignorForm(BasicForm):
    class Meta:
      model = Consignor
      fields = ['waiver_date', 'waiver_image', 'address', 'address2', 'city', 'state', 'zip', 'phone', 'image', 'pid_type', 'pid_image']

class EmployeeForm(BasicForm):
    class Meta:
      model = Employee
      fields = ['address', 'address2', 'city', 'state', 'zip', 'phone', 'date_of_birth', 'ice1_fname', 'ice1_lname', 'ice1_phone', 'ice1_relationship', 'ice2_fname', 'ice2_lname', 'ice2_phone', 'ice2_relationship', 'title', 'hourly_rate', 'start_date', 'end_date', 'exit_reason', 'image']	

def FORMS(request, form_name, instance=None):
  if TYPE(form_name) != 'Form': 
    return None
  form_class = globals()[form_name]
  model_class = form_class.Meta.model  
  if instance:
    if instance == 'u':
      instance = request.user
    elif instance == 'x':
      instance = request.user.extendeduser
    elif instance == 's':
      instance = request.user.extendeduser.shopper
    elif instance == 'c':
      instance = request.user.extendeduser.consignor
    elif instance == 'e':
      instance = request.user.extendeduser.employee
    else:
      pk = request.GET['pk'] if 'pk' in request.GET else request.POST['pk']
      instance = model_class.objects.get(pk=pk)    
    if request.method == 'GET': 
      return form_class(instance=instance)      
    return form_class(data=request.POST, files=request.FILES, instance=instance)

  # If not instance
  if request.method == 'GET':
    return form_class()
  return form_class(data=request.POST, files=request.FILES)

def META_FORMS(meta_form_name, request):
    meta_forms = []

    for f in SITE_DESIGN['MetaForm']:             
        if f['MetaForm'] == meta_form_name:
            dct = {}
            dct.update(f)
            dct.update({'FormName':f['Form']})
            dct.update({'Form':FORMS(request, f['Form'], f['Instance'])})
            dct.update({'FormDesign':FORM_DESIGN[f['Form']]})
            meta_forms.append(dct)    
    return meta_forms