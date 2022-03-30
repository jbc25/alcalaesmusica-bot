from django.conf import settings
from django.contrib.sites.models import Site
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Ownership(models.Model):
    site = models.OneToOneField(Site, on_delete=models.CASCADE, primary_key=True)

    company_name = models.CharField(_('Company name'), max_length=50, blank=True, null=True)
    company_department = models.CharField(_('Company department'), max_length=50, blank=True)
    first_name = models.CharField(_('First name'), max_length=30, blank=True, null=True)
    last_name = models.CharField(_('Last name'), max_length=30, blank=True, null=True)
    email = models.EmailField(_('Email'))

    street = models.CharField(_('Street'), max_length=100)
    postal_code = models.CharField(_('Postal code'), max_length=100)
    place = models.CharField(_('Place/City'), max_length=100)
    country_code = models.CharField(_('Country code'), max_length=2, default='CH')
    country_name = models.CharField(_('Country'), max_length=100, default='Switzerland')

    phone = models.CharField(_('Phone'), max_length=32, blank=True, null=True)
    fax = models.CharField(_('Fax'), max_length=32, blank=True, null=True)
    vat_number = models.CharField(_('VAT number'), max_length=32, blank=True, null=True)

    logo = models.ImageField(_('Logo'), upload_to='ownership', null=True, blank=True)
    logo_invoice = models.ImageField(_('Logo invoice'), upload_to='ownership', null=True, blank=True)

    stripe_public_key = models.CharField(_('Stripe public key'), max_length=32, blank=True, null=True)

    def __str__(self):
        return self.site.name

    @property
    def bankaccount(self):
        try:
            return self.bankaccounts.all()[0]
        except IndexError:
            return None

    @property
    def server_time(self):
        return timezone.now()


class BankAccount(models.Model):
    owner = models.ForeignKey(Ownership, on_delete=models.CASCADE, related_name='bankaccounts')
    name = models.CharField(_('Name'), max_length=100)

    street = models.CharField(_('Street'), max_length=100)
    postal_code = models.CharField(_('Postal code'), max_length=100)
    place = models.CharField(_('Place/City'), max_length=100)
    country_code = models.CharField(_('Country code'), max_length=2, default='CH')
    country_name = models.CharField(_('Country'), max_length=100, default='Switzerland')

    iban = models.CharField(_('IBAN'), max_length=42, blank=True)
    number = models.CharField(_('Number'), max_length=42, blank=True)
    bic = models.CharField(_('BIC'), max_length=11, blank=True)

    currency_code = models.CharField(_('Currency ISO code'), max_length=3, default='CHF')

    def __str__(self):
        return self.name

