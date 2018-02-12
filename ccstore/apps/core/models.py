import codecs
import datetime
import uuid

from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.dispatch import receiver
from django.utils.timezone import now
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from cc.models import Wallet, Operation

from . import rpc_pb2 as ln
from . import rpc_pb2_grpc as lnrpc
from .util import get_default_currency, from_satoshi


User = get_user_model()


class AbstractProxyWallet(models.Model):
    wallet = models.ForeignKey(Wallet)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    @property
    def balance(self):
        return self.wallet.balance

    class Meta:
        abstract = True


class UserProxyWallet(AbstractProxyWallet):
    user = models.OneToOneField(User, related_name="proxywallet")

    def __str__(self):
        return str(self.user)


class SiteProxyWallet(AbstractProxyWallet):
    site = models.OneToOneField(Site, related_name="proxywallet")
    wallet = models.ForeignKey(Wallet)

    def __str__(self):
        return str(self.site)


PAYMENT_STATUS_CHOICES = (
    ('pending_payment', _('Pending Payment')),
    ('complete', _('Complete')),
    ('expired', _('Expired')),
    ('error', _('Error')),
)


def _default_currency():
    return get_default_currency().ticker


class AbstractPayment(models.Model):
    """
    Abstract model for payment requests.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User)
    order_number = models.CharField(max_length=128, db_index=True, null=True)
    satoshi_amount = models.IntegerField(blank=True, default=0)
    coin_price = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    currency = models.CharField(_('Currency'), max_length=12, default=_default_currency)
    status = models.CharField(max_length=50, default='pending_payment', choices=PAYMENT_STATUS_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    @property
    def expiration(self):
        return self.created + datetime.timedelta(seconds=settings.CCSTORE_PAYMENT_EXPIRE)

    @property
    def amount(self):
        return from_satoshi(self.satoshi_amount)

    @property
    def wallet(self):
        return self.user.proxywallet.wallet

    @property
    def address(self):
        return self.wallet.get_address()

    class Meta:
        abstract = True

    def __str__(self):
        return self.order_number


class Payment(AbstractPayment):
    def get_payment_operation(self):
        try:
            return Operation.objects.filter(
                wallet=self.wallet,
                balance=from_satoshi(self.satoshi_amount),
                created__gte=self.created
            ).order_by('created')[0]
        except IndexError:
            return

    def check_payment(self, save=True):
        operation = self.get_payment_operation()
        if not operation:
            if now() >= self.expiration:
                self.status = 'expired'
            else:
                self.status = 'pending_payment'
        else:
            if operation.created >= self.expiration:
                # TODO: Notify user of expired payment received, to get refund or spend wallet balance.
                self.status = 'expired'
            else:
                self.status = 'complete'
        if save:
            self.save()


class LightningPayment(models.Model):
    r_hash = models.CharField(max_length=64)
    payment_request = models.CharField(max_length=1000)
    status = models.CharField(max_length=50, default='pending_invoice', choices=PAYMENT_STATUS_CHOICES)

    def generate_invoice(self):
        """
        Generates a new invoice
        """
        if self.status != 'pending_invoice':
            return False

        channel = ln.insecure_channel(settings.LND_RPCHOST)
        stub = lnrpc.LightningStub(channel)

        add_invoice_resp = stub.AddInvoice(lnrpc.Invoice(value=self.satoshi_amount,
                                                         memo="User {} | Order {}".format(self.user.email,
                                                                                          self.order_number)))

        r_hash_base64 = codecs.encode(add_invoice_resp.r_hash, 'base64')
        self.r_hash = r_hash_base64.decode('utf-8')
        self.payment_request = add_invoice_resp.payment_request
        self.status = 'pending_payment'
        self.save()

    def check_payment(self):
        """
        Checks if the Lightning payment has been received for this invoice order
        """
        if self.status == 'pending_invoice':
            return False

        channel = ln.insecure_channel(settings.LND_RPCHOST)
        stub = lnrpc.LightningStub(channel)

        r_hash_base64 = self.r_hash.encode('utf-8')
        r_hash_bytes = str(codecs.decode(r_hash_base64, 'base64'))
        invoice_resp = stub.LookupInvoice(lnrpc.PaymentHash(r_hash=r_hash_bytes))

        if invoice_resp.settled:
            # Payment complete
            self.status = 'complete'
            self.save()
            return True
        else:
            # Payment not received
            return False


# Signals receivers

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
