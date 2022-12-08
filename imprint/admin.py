from django.contrib import admin

from . import models


class OwnershipAdmin(admin.ModelAdmin):
    list_display = ('site', 'first_name', 'last_name', 'company_name', 'country_code')


class BankAccountAdmin(admin.ModelAdmin):
    list_display = ('owner', 'country_code', 'iban', 'bic')
    list_filter = ('owner', )


admin.site.register(models.Ownership, OwnershipAdmin)
admin.site.register(models.BankAccount, BankAccountAdmin)
