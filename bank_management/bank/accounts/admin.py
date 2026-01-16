from django.contrib import admin
from .models import Profile, Account

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'branch', 'account_number', 'balance','reply','message','upi_id','disable_request','disable_approved')
    list_filter = ('role', 'branch')
    search_fields = ('user__username', 'user__email', 'account_number')

    # This is just for admin display
    def account_number(self, obj):
        return obj.user.account.account_number
    account_number.short_description = 'Account Number'

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_number', 'created_at')
    search_fields = ('user__username', 'account_number')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Account, AccountAdmin)
