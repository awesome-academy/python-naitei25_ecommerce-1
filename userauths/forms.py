from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from userauths.models import User
from core.constants import ROLE_CHOICES
from userauths.models import User,Profile
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MaxLengthValidator

class UserRegisterForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": _("Username")}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": _("Email")}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("Password")}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": _("Confirm Password")}))
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.Select())

    class Meta:
        model = User
        fields = ['username', 'email', 'role']

class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        label="Full name",
        required=True,
        validators=[MinLengthValidator(2), MaxLengthValidator(50)],
        widget=forms.TextInput(attrs={"placeholder": "Full Name"})
    )

    bio = forms.CharField(
        label="Bio",
        required=False,
        validators=[MaxLengthValidator(100)],
        widget=forms.Textarea(attrs={"placeholder": "Bio", "rows": 3})
    )

    phone = forms.CharField(
        label="Phone",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Phone"})
    )

    class Meta:
        model = Profile
        fields = ["full_name", "image", "bio", "phone"]
