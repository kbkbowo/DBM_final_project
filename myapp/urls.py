from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('signup/', views.signup, name='signup'),
    path('admin_home/', views.admin_home, name='admin_home'),
    path('manage_users/', views.manage_users, name='manage_users')
]