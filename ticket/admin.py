from django.contrib import admin
from ticket import models

# Register your models here.

@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    ...