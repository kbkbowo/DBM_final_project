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
    path('org_home/<str:org_id>/event_panel/', views.org_event_panel, name='org_event_panel'),
    path('org_home/<str:org_id>/event_panel/create_event/', views.org_create_event, name='org_create_event'),
    path('org_home/<str:org_id>/event_panel/<str:event_id>/delete_event/', views.org_delete_event, name='org_delete_event'),
    path('event/', views.event, name='event'),
    path('event_browse/', views.event_browse, name='event_browse'),
    path('event/<str:event_id>/join', views.event_join, name='event_join'),
]