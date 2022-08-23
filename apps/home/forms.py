# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.forms import ModelForm
from .models import Employee

# Create a venue form
class EmployeeForm(ModelForm):
	class Meta:
		model = Employee
		fields = ('img', 'location', 'birth_date')