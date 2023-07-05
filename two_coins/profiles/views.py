from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView, LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView

from . import forms
from .forms import CustomUserCreationForm


class ProfileEditView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
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


class CustomLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        messages.info(request, f"Logged out.")
        return super().get(request, *args, **kwargs)


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = AuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        login(self.request, form.get_user())
        messages.success(self.request, f"Logged in as {form.cleaned_data.get('username')}.")
        return redirect("account_list")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return self.render_to_response(self.get_context_data(form=form))


class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('account_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, "User created successfully!")
            messages.info(self.request, f"Logged in as {username}.")
        return response

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong.")
        return super().form_invalid(form)


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
