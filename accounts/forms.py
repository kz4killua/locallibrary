from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from catalog.forms import StyledValidation


class RegistrationForm(StyledValidation, UserCreationForm):
    """A form to create an account for a user. """

    def __init__(self, *args):
        super().__init__(*args)
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    class Meta(UserCreationForm.Meta):
        model = get_user_model()


class LoginForm(AuthenticationForm):
    """A form to login a user. """
    username = forms.CharField(
        widget = forms.TextInput(
            attrs={'class': "form-control", 'id': "floatingInput", 'placeholder': "Username"}
        ),
    )
    password = forms.CharField(
        widget = forms.PasswordInput(
            attrs={'class': "form-control", 'id': "floatingPassword", 'placeholder': "Password"}
        )
    )