from oscar.core.loading import get_model
from oscar.apps.checkout.views import PaymentDetailsView as OscarPaymentDetailsView

from apps.core.models import Payment
from apps.core.facade import PaymentFacade
from apps.core.util import get_crypto_price, fiat_to_crypto, crypto_to_fiat, to_satoshi


Order = get_model('order', 'Order')
Source = get_model('payment', 'Source')
SourceType = get_model('payment', 'SourceType')


class PaymentDetailsView(OscarPaymentDetailsView):
    def get_order_number(self, basket):
        order_number = self.checkout_session.get_order_number()
        if not order_number:
            order_number = self.generate_order_number(basket)
            self.checkout_session.set_order_number(order_number)
        return order_number

    def handle_payment(self, order_number, total, **kwargs):
        payment = PaymentFacade().check_order_payment(order_number, self.request.user)
        source_type, created = SourceType.objects.get_or_create(name='ccstore')
        currency = self.request.basket.currency
        source = Source(
            source_type=source_type,
            currency=currency,
            amount_allocated=crypto_to_fiat(payment.amount),
            amount_debited=total.incl_tax,
            reference=payment.id
        )
        self.add_payment_source(source)
        self.add_payment_event('purchase', total.incl_tax)

    def get_payment_object(self, basket, order_number):
        amount = basket.total_incl_tax
        coin_price = get_crypto_price()
        cc_amount = fiat_to_crypto(amount, price=coin_price)
        satoshi_amount = to_satoshi(cc_amount)
        try:
            payment = Payment.objects.get(
                order_number=order_number,
                status='pending_payment',
                user=self.request.user
            )
        except Payment.DoesNotExist:
            payment = Payment(
                user=self.request.user,
                order_number=order_number,
                satoshi_amount=satoshi_amount,
                coin_price=coin_price,
                status='pending_payment'
            )
            payment.save()
        return payment

    def get_context_data(self, **kwargs):
        ctx = super(PaymentDetailsView, self).get_context_data(**kwargs)
        order_number = self.get_order_number(self.request.basket)
        ctx['payment'] = self.get_payment_object(self.request.basket, order_number)
        return ctx
