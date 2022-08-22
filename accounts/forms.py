from django.contrib.auth import get_user_model
from django import forms

from .models import Userr

class UserCreationForm(forms.ModelForm):
    password = forms.CharField()

    class Meta:
        model = get_user_model()
        fields = ('email','clerkname','personalimage','introduction_text',)
    
    def clean_password(self):
        password = self.cleaned_data.get("password")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


#############################################################################################
class ProfileForm(forms.Form):
    clerkname = forms.CharField(max_length=20, label='名前')
    email = forms.EmailField(max_length=250, label='メールアドレス')
    introduction_text = forms.CharField(label='自己紹介', widget=forms.Textarea(), required=False)
    personalimage = forms.ImageField(required=False)