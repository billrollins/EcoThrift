# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    bio = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Bio",
                "class": "form-control"
            }
        ))
    location  = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Location ",
                "class": "form-control"
            }
        ))
    birth_date  = forms.DateField(
        widget=forms.DateInput(
            attrs={
                "placeholder": "Birth Date",
                "class": "form-control"
            }
        ))

    class Meta:
        model = Profile
        fields = ('bio', 'location', 'birth_date')
