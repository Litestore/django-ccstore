from django.contrib import admin

from .models import SiteProxyWallet, UserProxyWallet


class SiteProxyWalletAdmin(admin.ModelAdmin):
    list_display = ('site', 'wallet', 'created', 'updated')


class UserProxyWalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'wallet', 'created', 'updated')


admin.site.register(SiteProxyWallet, SiteProxyWalletAdmin)
admin.site.register(UserProxyWallet, UserProxyWalletAdmin)
