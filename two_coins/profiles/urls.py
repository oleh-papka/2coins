from django.urls import path
from two_coins.settings import ENABLE_AUTH0

from . import views
from .views import Auth0LoginView, Auth0CallbackView, Auth0LogoutView

urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name="profile"),
    path('profile/edit/', views.ProfileEditView.as_view(), name="profile_edit"),
]

if ENABLE_AUTH0:
    urlpatterns += [
        path('login/', Auth0LoginView.as_view(), name='login'),
        path('callback/', Auth0CallbackView.as_view(), name='auth0_callback'),
        path('logout/', Auth0LogoutView.as_view(), name='logout'),
    ]
else:
    urlpatterns += [
        path('login/', views.CustomLoginView.as_view(), name="login"),
        path('logout/', views.CustomLogoutView.as_view(), name="logout"),
        path('register/', views.CustomRegisterView.as_view(), name="register"),
    ]
