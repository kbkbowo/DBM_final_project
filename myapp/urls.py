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
    path('org_browse/', views.org_browse, name='org_browse'),
    path('org_home/<str:org_id>/', views.org_page, name='org_page'),
    path('org_home/<str:org_id>/edit_info/', views.org_edit_info, name='org_edit_info'),
    path('org_home/<str:org_id>/edit_founder/', views.org_edit_founder, name='org_edit_founder'),
    path('org_home/<str:org_id>/delete/', views.org_delete, name='org_delete'),
    path('org_home/<str:org_id>/leave/', views.org_leave, name='org_leave'),
    path('org_home/<str:org_id>/join/', views.org_join, name='org_join'),
]