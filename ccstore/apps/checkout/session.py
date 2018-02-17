from oscar.apps.checkout.session import CheckoutSessionMixin as OscarCheckoutSessionMixin

from apps.core.models import Payment


class CheckoutSessionMixin(OscarCheckoutSessionMixin):
    def get_payment_uuid(self):
        return self.checkout_session._get('payment', 'uuid')

    def set_payment_uuid(self, uuid):
        self.checkout_session._set('payment', 'uuid', uuid)

    def build_submission(self, **kwargs):
        submission = super().build_submission(**kwargs)
        uuid = self.get_payment_uuid()
        if uuid:
            try:
                payment = Payment.objects.get(id=uuid)
            except Payment.DoesNotExist:
                payment = None
            submission['payment'] = payment
        return submission
