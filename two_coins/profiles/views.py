from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import UpdateView, CreateView, TemplateView

from two_coins import settings
from .forms import CustomUserCreationForm, ProfileForm, CustomAuthenticationForm
from .models import Profile, CustomUser

if settings.ENABLE_AUTH0:
    from authlib.integrations.django_client import OAuth
    from urllib.parse import urlencode, quote_plus

    oauth = OAuth()

    oauth.register(
        "auth0",
        client_id=settings.AUTH0_CLIENT_ID,
        client_secret=settings.AUTH0_CLIENT_SECRET,
        client_kwargs={
            "scope": "openid profile email",
        },
        server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
    )


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
        return redirect("dashboard")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return self.render_to_response(self.get_context_data(form=form))


class Auth0LoginView(View):
    """Handles the redirect to the Auth0 login page."""

    def get(self, request, *args, **kwargs):
        return oauth.auth0.authorize_redirect(
            request, request.build_absolute_uri(reverse("auth0_callback"))
        )


class Auth0CallbackView(View):
    """Handles the callback from Auth0 after authentication."""

    def get(self, request, *args, **kwargs):
        token = oauth.auth0.authorize_access_token(request)
        user_info = token.get("userinfo")

        # Link Auth0 user with Django user model
        django_user, created = CustomUser.objects.get_or_create(
            email=user_info["email"],
        )
        login(request, django_user)

        # Store user in the session
        request.session["user"] = django_user.id
        messages.success(request, "Successfully logged in!")
        return redirect(reverse("dashboard"))


class Auth0LogoutView(View):
    """Handles logout and redirection to the Auth0 logout endpoint."""

    def get(self, request, *args, **kwargs):
        request.session.clear()
        messages.info(request, "Successfully logged out!")
        return redirect(
            f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
            + urlencode(
                {
                    "returnTo": request.build_absolute_uri(reverse("login")),
                    "client_id": settings.AUTH0_CLIENT_ID,
                },
                quote_via=quote_plus,
            ),
        )


class CustomRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('dashboard')

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
