from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import UpdateView, CreateView, TemplateView

from .forms import CustomUserCreationForm, ProfileForm, CustomAuthenticationForm
from .models import Profile


class ProfileView(TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.get(user=self.request.user)

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    login_url = 'login'
    form_class = ProfileForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('profile_edit')

    def get_object(self, queryset=None):
        return Profile.objects.get(user=self.request.user)

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, "User updated successfully!")
        return super().form_valid(form)


class CustomLogoutView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        messages.info(request, "Logged out.")
        logout(request)
        return redirect(reverse_lazy('login'))


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm
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
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=email, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, "User created successfully!")
            messages.info(self.request, f"Logged in as {email}.")
        return response

    def form_invalid(self, form):
        messages.warning(self.request, "Something went wrong.")
        return super().form_invalid(form)
