from django.contrib import admin
from .models import Category, Priority, HELPForm

# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Customize this as needed

@admin.register(Priority)
class PriorityAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Customize this as needed


@admin.register(HELPForm)
class HELPFormAdmin(admin.ModelAdmin):
    list_display = ('subject', 'user', 'status', 'date_submitted', 'admin_response', 'response_timestamp', 'rating')
    search_fields = ['subject', 'complaint']
    list_filter = ['status', 'rating']
