from django.contrib import admin
from .models import EmailConfirmation

@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'confirmed_at', 'is_valid')
    list_filter = ('confirmed_at', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('token', 'created_at', 'confirmed_at')
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Válido'