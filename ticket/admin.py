from django.contrib import admin
from ticket import models

# Register your models here.

@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = 'id', 'title', 'description', 'priority','user', 'created_date', 'show',
    ordering = '-id',
    search_fields = 'id', 'title', 'description', 'priority', 'user',
    list_display_links = 'id',
    list_editable = 'show',
    list_filter = 'created_date',
    list_per_page = 10
    list_max_show_all = 200

@admin.register(models.Priority)
class TicketAdmin(admin.ModelAdmin):
    list_display = 'name',