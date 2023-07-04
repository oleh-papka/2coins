from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from . import forms
from .forms import CustomUserCreationForm


class ProfileEditView(UpdateView):
    form_class = forms.ProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        return self.request.user.profile

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['instance_name'] = 'Profile'
        return context


def logout_view(request):
    logout(request)
    messages.info(request, f"Logged out.")

    return redirect('login')


def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in as {username}.")
                return redirect("account_list")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            messages.success(request, "User created successfully!")
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.info(request, f"Logged in as {username}.")

            return redirect('account_list')
        else:
            messages.warning(request, "Something went wrong.")

        return redirect('register')
    else:
        form = CustomUserCreationForm()

    return render(request, 'users/register.html', {'form': form})
