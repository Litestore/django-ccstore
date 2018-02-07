import logging

from oscar.apps.payment import exceptions

from .models import Payment


logger = logging.getLogger('ccstore.payment')


class PaymentFacade:
    def check_order_payment(self, order_number, user):
        try:
            payment = Payment.objects.filter(
                order_number=order_number,
                user=user
            ).order_by('-created')[0]
        except IndexError:
            logger.info("Payment object not available for {}".format(order_number))
            raise exceptions.UnableToTakePayment

        if payment.status == 'pending_payment':
            payment.check_payment(save=True)

        if payment.status == 'complete':
            logger.info("Payment received for {}".format(order_number))
            return payment
        elif payment.status == 'expired':
            logger.info("Payment expired for {}".format(order_number))
            raise exceptions.UnableToTakePayment
        else:
            logger.info("Payment not received for {}".format(order_number))
            raise exceptions.InsufficientPaymentSources(payment.status)
