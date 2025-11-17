from django.contrib import admin
from . import models

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')
    search_fields = ('name',)
    list_display_links = ('id', 'name')
    ordering = ('name',)

@admin.register(models.Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'description')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    list_display_links = ('id', 'name')
    ordering = ('category', 'name')

@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'status', 'priority', 'owner', 'assigned_to', 'created_date', 'show')
    ordering = ('-id',)
    search_fields = ('id', 'title', 'description', 'owner__username', 'assigned_to__username')
    list_display_links = ('id', 'title')
    list_filter = ('created_date', 'status', 'priority', 'category', 'assigned_to')
    list_editable = ('show', 'status')
    list_per_page = 20

@admin.register(models.TicketEvent)
class TicketEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'event_type', 'created_date')
    list_display_links = ('id', 'ticket')
    list_filter = ('event_type', 'created_date', 'user')
    search_fields = ('description', 'ticket__title', 'user__username')
    readonly_fields = ('ticket', 'user', 'event_type', 'description', 'created_date')

    def has_add_permission(self, request):
        return False