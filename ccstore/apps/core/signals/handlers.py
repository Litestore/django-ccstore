from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site

from cc.models import Wallet

from apps.core.models import UserProxyWallet, SiteProxyWallet
from apps.core.util import get_default_currency

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        currency = get_default_currency()
        wallet = Wallet.objects.create(currency=currency)
        UserProxyWallet.objects.create(user=instance, wallet=wallet)


@receiver(post_save, sender=Site)
def create_site_wallet(sender, instance, created, **kwargs):
    if created:
        currency = get_default_currency()
        wallet = Wallet.objects.create(currency=currency)
        SiteProxyWallet.objects.create(site=instance, wallet=wallet)
