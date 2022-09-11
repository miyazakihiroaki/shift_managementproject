from django.contrib.auth import get_user_model
from django import forms

from accounts.models import Userr

class StaffSelectForm(forms.ModelForm):
    brand_cd = forms.ModelChoiceField(queryset=Userr.objects.all())
    class Meta:
        model = Userr
        fields = ('clerkname',)