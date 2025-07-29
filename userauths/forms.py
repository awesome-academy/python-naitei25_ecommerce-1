from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from userauths.models import User


class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": _("Username")}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": _("Email")}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("Password")}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("Confirm Password")}))

    class Meta:
        model = User
        fields = ['username', 'email']
