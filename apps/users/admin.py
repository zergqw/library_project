from django.contrib import admin

from .models import Reader


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ('user', 'ticket_number', 'phone')
    search_fields = ('ticket_number', 'user__last_name')
