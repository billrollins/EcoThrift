from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from .models import *

class BasicCustomForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.model = self._meta.model
		self.form_struct = self.model.form_struct
		for f in self.model.form_fields: self.fields[f].widget.attrs['class'] = 'form-control'
		for f, t in self.model.form_type: 
			self.fields[f].widget.input_type = t
			if t == 'tel':
				self.fields[f].widget.template_name = 'widgets/phone.html'
			elif t == 'img1':
				self.fields[f].widget.template_name = 'widgets/image_input.html'
			elif t == 'chk':
				self.fields[f].widget.template_name = 'widgets/switch.html'

class StoreForm(BasicCustomForm):
	prefix = 'store'
	class Meta:
		model = Store
		fields = model.form_fields

class DepartmentForm(BasicCustomForm):
	prefix = 'department'
	class Meta:
		model = Department
		fields = model.form_fields

class PositionForm(BasicCustomForm):
	prefix = 'position'
	class Meta:
		model = Position
		fields = model.form_fields

class SectionForm(BasicCustomForm):
	prefix = 'section'
	class Meta:
		model = Section
		fields = model.form_fields

class OrderForm(BasicCustomForm):
	prefix = 'order'
	class Meta:
		model = Order
		fields = model.form_fields

class DropoffForm(BasicCustomForm):
	prefix = 'dropoff'
	class Meta:
		model = Dropoff
		fields = model.form_fields

class LiquidatorForm(BasicCustomForm):
	prefix = 'liquidator'
	class Meta:
		model = Liquidator
		fields = model.form_fields

class BasicUserForm(BasicCustomForm):
	prefix = 'user'
	class Meta:
		model = BasicUser
		fields = model.form_fields

class EmployeeForm(BasicCustomForm):
	prefix = 'employee'
	class Meta:
		model = Employee
		fields = model.form_fields

class ShopperForm(BasicCustomForm):
	prefix = 'shopper'
	class Meta:
		model = Shopper
		fields = model.form_fields

class ConsignorForm(BasicCustomForm):
	prefix = 'consignor'
	class Meta:
		model = Consignor
		fields = model.form_fields