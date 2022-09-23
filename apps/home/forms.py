from .models import *

class BasicForm(ModelForm):
  model, model_name = None, ''
  form_name, form_design = '', None
  field_attrs, field_struct = [], []
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)  
    for nm, attrs, temp in self.field_attrs:
      if temp:
        self.fields[nm].widget.template_name = temp
      for k, v in attrs.items(): 
        if v: self.fields[nm].widget.attrs[k.lower()] = v
    return

#############################################################
# Paste Form Code Below this line
#############################################################	

class LiquidatorForm(BasicForm):
    form_name = 'LiquidatorForm'
    form_design = FORM_DESIGN['LiquidatorForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Liquidator
    model_name = 'Liquidator'
    class Meta:
      model = Liquidator
      fields = ['name', 'description', 'website', 'contact_phone', 'contact_email']

class StoreForm(BasicForm):
    form_name = 'StoreForm'
    form_design = FORM_DESIGN['StoreForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Store
    model_name = 'Store'
    class Meta:
      model = Store
      fields = ['name', 'general_manager', 'address', 'address2', 'city', 'state', 'zip', 'phone', 'email']

class DepartmentForm(BasicForm):
    form_name = 'DepartmentForm'
    form_design = FORM_DESIGN['DepartmentForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Department
    model_name = 'Department'
    class Meta:
      model = Department
      fields = ['store', 'name', 'department_manager']

class SectionForm(BasicForm):
    form_name = 'SectionForm'
    form_design = FORM_DESIGN['SectionForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Section
    model_name = 'Section'
    class Meta:
      model = Section
      fields = ['store', 'name', 'description']

class LocationForm(BasicForm):
    form_name = 'LocationForm'
    form_design = FORM_DESIGN['LocationForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Location
    model_name = 'Location'
    class Meta:
      model = Location
      fields = ['section', 'label']

class PositionForm(BasicForm):
    form_name = 'PositionForm'
    form_design = FORM_DESIGN['PositionForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Position
    model_name = 'Position'
    class Meta:
      model = Position
      fields = ['department', 'name']

class DropoffForm(BasicForm):
    form_name = 'DropoffForm'
    form_design = FORM_DESIGN['DropoffForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Dropoff
    model_name = 'Dropoff'
    class Meta:
      model = Dropoff
      fields = ['employee', 'consignor', 'date', 'comments', 'agreement_image', 'offer_amount']

class OrderForm(BasicForm):
    form_name = 'OrderForm'
    form_design = FORM_DESIGN['OrderForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Order
    model_name = 'Order'
    class Meta:
      model = Order
      fields = ['order_number', 'purchase_date', 'liquidator', 'category', 'item_count', 'pallet_count', 'sale_amount', 'shipping_amount', 'delivery_date', 'accepted_by', 'unloaded_by', 'pod_image', 'manifest_file']

class ItemForm(BasicForm):
    form_name = 'ItemForm'
    form_design = FORM_DESIGN['ItemForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Item
    model_name = 'Item'
    class Meta:
      model = Item
      fields = ['employee', 'order', 'dropoff', 'created_date', 'zero_date', 'change_date', 'section', 'description', 'brand', 'condition', 'tested', 'tags', 'price_code', 'static_price', 'expected_price', 'status_change']

class UserForm(BasicForm):
    form_name = 'UserForm'
    form_design = FORM_DESIGN['UserForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = User
    model_name = 'User'
    class Meta:
      model = User
      fields = ['first_name', 'last_name', 'email']

class ShopperForm(BasicForm):
    form_name = 'ShopperForm'
    form_design = FORM_DESIGN['ShopperForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Shopper
    model_name = 'Shopper'
    class Meta:
      model = Shopper
      fields = ['email_preferences', 'waiver_date', 'waiver_image']

class ConsignorForm(BasicForm):
    form_name = 'ConsignorForm'
    form_design = FORM_DESIGN['ConsignorForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Consignor
    model_name = 'Consignor'
    class Meta:
      model = Consignor
      fields = ['address', 'address2', 'city', 'state', 'zip', 'phone', 'waiver_date', 'waiver_image', 'image', 'pid_type', 'pid_image']

class EmployeeForm(BasicForm):
    form_name = 'EmployeeForm'
    form_design = FORM_DESIGN['EmployeeForm']
    field_struct, field_attrs = GET_FORM_FIELDS(form_design)
    model_class = Employee
    model_name = 'Employee'
    class Meta:
      model = Employee
      fields = ['title', 'hourly_rate', 'address', 'address2', 'city', 'state', 'zip', 'phone', 'date_of_birth', 'ice1_fname', 'ice1_lname', 'ice1_phone', 'ice1_relationship', 'ice2_fname', 'ice2_lname', 'ice2_phone', 'ice2_relationship', 'start_date', 'end_date', 'exit_reason', 'image']

FORMS = {'LiquidatorForm':LiquidatorForm, 'StoreForm':StoreForm, 'DepartmentForm':DepartmentForm, 'SectionForm':SectionForm, 'LocationForm':LocationForm, 'PositionForm':PositionForm, 'DropoffForm':DropoffForm, 'OrderForm':OrderForm, 'ItemForm':ItemForm, 'UserForm':UserForm, 'ShopperForm':ShopperForm, 'ConsignorForm':ConsignorForm, 'EmployeeForm':EmployeeForm}	

##################################################################################################################
# Form Functions
##################################################################################################################

def GET_META_FORM(request, name):
    COLS = ['Header','SubHeader','Button','Redirect_Valid','Redirect_Invalid','Delete', 'Instance', 'Form']
    df = META_FORMS[META_FORMS.Name == name]
    template = loader.get_template(df.Template.iloc[0])
    meta_forms = []
    pks = request.GET['pk'].split(';') if 'pk' in request.GET else ['']*df.shape[0]
    for pk, (_, meta) in zip(pks, df.iterrows()):
      meta_form = meta[COLS]
      form_class = FORMS[meta['Form']]
      if meta['Instance'] != 'pk':
        pk = meta['Instance']
      instance = GET_FORM_INSTANCE(request, pk, form_class.model)
      meta_form['thisForm'] = form_class(instance=instance)
      meta_form['pk'] = pk
      meta_forms.append(meta_form)
    return template, meta_forms

def GET_FORM_INSTANCE(request, pk='', model=None):
    cur_dict = {
        'cur_user': request.user,
        'cur_shp':  request.user.extendeduser.shopper,
        'cur_con':  request.user.extendeduser.consignor,
        'cur_emp':  request.user.extendeduser.employee,
        '':  None
    }
    if pk in cur_dict:
      return cur_dict[pk]
    if model:
      return model.objects.get(**{model._pk_:pk})
    return None