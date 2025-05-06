from django.urls import path
from . import views


app_name = 'helpdesk'
urlpatterns = [
    path('', views.home, name="home"),
    path('new-ticket', views.create_help_form, name="new_ticket"),
    path('list-ticket', views.help_list, name="help_list"),
    path('IT-list-ticket', views.it_help_list, name="it_help_list"),
    path('categories/', views.category_list, name='category-list'),
    path('categories/create/', views.category_create, name='category-create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category-edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category-delete'),
    path('priority/', views.priority_list, name='priority-list'),
    path('priority/create/', views.priority_create, name='priority-create'),
    path('priority/<int:pk>/edit/', views.priority_edit, name='priority-edit'),
    path('priority/<int:pk>/delete/', views.priority_delete, name='priority-delete'),
    path('ticket-others/', views.ticket_others, name='ticket_others'),
    path('admin-dashboard/', views.admin_dash, name='admin_dash'),
    path('ticket/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('close_complainant/<int:pk>/', views.close_complainant, name='close_complainant'),
    path('ticket/rate/<int:pk>/', views.rate_ticket_response, name='rate_ticket_response'),
    path('ticket/reply/<int:pk>/', views.admin_reply_ticket, name='admin_reply_ticket'),
    path('report/', views.report_page, name='report_page'),
    path('export/excel/', views.export_to_excel, name='export_to_excel'),
    path('export/pdf/', views.export_to_pdf, name='export_to_pdf'),
]