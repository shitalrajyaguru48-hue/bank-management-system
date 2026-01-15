from django.contrib import admin
from .models import Statement

@admin.register(Statement)
class StatementAdmin(admin.ModelAdmin):
    list_display = ('customer', 'transaction_type', 'amount', 'balance_after', 'created_at')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('customer__user__username', 'customer__user__email')
    ordering = ('-created_at',)
