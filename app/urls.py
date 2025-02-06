from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('client/', views.clientDashboard, name="client"),
    path('supervisor/', views.supervisorDashboard, name="supervisor"),
    path('manager/', views.managerDashboard, name="manager"),
    path('createform/', views.create_ptw_form, name='create_form'),
    path('list/', views.form_list, name='form_list'),
    path('delete_form/<int:pk>/', views.delete_form, name='delete_form'),
    path('view_form/<int:pk>/', views.view_form, name='view_form'),
    path('approve/supervisor/<int:pk>/', views.approve_supervisor, name='approve_supervisor'),
    path('approve/manager/<int:pk>/', views.approve_manager, name='approve_manager'),
    path('disapprove-supervisor/<int:pk>/', views.disapprove_supervisor, name='disapprove_supervisor'),
    path('disapprove-manager/<int:pk>/', views.disapprove_manager, name='disapprove_manager'),
    path('edit_form/<int:pk>/', views.edit_form, name='edit_form'),
    path('create_nhis/', views.create_nhis_form, name='create_nhis'),
    path('nhis_list/', views.nhis_list, name='nhis_list'),
    path('edit_nhis_form/<int:pk>/', views.edit_nhis_form, name='edit_nhis_form'),
    path('delete_nhis_form/<int:pk>/', views.delete_nhis_form, name='delete_nhis_form'),
    path('approve_nhis/supervisor/<int:pk>/', views.approve_nhis_supervisor, name='approve_nhis_supervisor'),
    path('approve_nhis/manager/<int:pk>/', views.approve_nhis_manager, name='approve_nhis_manager'),
    path('disapprove_nhis-supervisor/<int:pk>/', views.disapprove_nhis_supervisor, name='disapprove_nhis_supervisor'),
    path('disapprove_nhis-manager/<int:pk>/', views.disapprove_nhis_manager, name='disapprove_nhis_manager'),
    path('form-report/', views.form_report, name='form_report'),
    path('view_nhis_form/<int:pk>/', views.view_nhis_form, name='view_nhis_form'),

]