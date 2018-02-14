from oscar.apps.checkout.session import CheckoutSessionMixin as OscarCheckoutSessionMixin

from apps.core.models import Payment
from apps.core.util import get_crypto_price, fiat_to_crypto, to_satoshi


class CheckoutSessionMixin(OscarCheckoutSessionMixin):
    def get_order_number(self, basket):
        order_number = self.checkout_session.get_order_number()
        if not order_number:
            order_number = self.generate_order_number(basket)
            self.checkout_session.set_order_number(order_number)
        return order_number

    def get_payment_object(self, basket, order_number, user=None, save=True):
        if not user:
            user = self.request.user
        amount = basket.total_incl_tax
        coin_price = get_crypto_price()
        cc_amount = fiat_to_crypto(amount, price=coin_price)
        satoshi_amount = to_satoshi(cc_amount)
        try:
            payment = Payment.objects.get(
                order_number=order_number,
                status='pending_payment',
                user=user
            )
        except Payment.DoesNotExist:
            payment = Payment(
                user=user,
                order_number=order_number,
                satoshi_amount=satoshi_amount,
                coin_price=coin_price,
                status='pending_payment'
            )
            if save:
                payment.save()
        return payment

    def build_submission(self, **kwargs):
        submission = super().build_submission(**kwargs)
        user = submission['user']
        basket = submission['basket']
        order_number = self.get_order_number(basket)
        payment = self.get_payment_object(basket, order_number, user=user, save=False)
        if payment.pk:
            # Payment object should be created only when accessing PaymentDetailsView
            submission['payment'] = payment
        return submission
