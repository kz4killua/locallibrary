from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import get_user_model, login
from django.urls import reverse
from django.contrib.auth.views import LoginView, LogoutView

from .forms import LoginForm, RegistrationForm


User = get_user_model()


def register(request):
    """Creates an account for a user."""
    if request.method == "GET":
        return render(request, "accounts/register.html", {
            "form": RegistrationForm()
        })
    else:
        form = RegistrationForm(request.POST)
        # Make sure the form is valid
        if not form.is_valid():
            return render(request, "accounts/register.html", {
                "form": form
            })
        # Create a new user
        user = User.objects.create_user(
            username = form.cleaned_data['username'],
            password = form.cleaned_data['password1']
        )
        user.save()
        # Log the user in
        login(request, user)
        return HttpResponseRedirect(reverse("catalog:index"))


class Login(LoginView):
    """Logs in a user."""
    template_name = 'accounts/login.html'
    authentication_form = LoginForm


class Logout(LogoutView):
    """Logs out a user."""
    pass