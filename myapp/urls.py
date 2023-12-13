from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('signup/', views.signup, name='signup'),
    path('manage_users/', views.manage_users, name='manage_users'),
    path('org_home/', views.org_home, name='org_home'),
    path('org_build/', views.org_build, name='org_build'),
]