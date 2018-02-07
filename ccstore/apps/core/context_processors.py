from django.conf import settings

from .util import get_crypto_price


def default(request):
    return {
        'DEFAULT_COIN_PRICE': get_crypto_price(),
        'CCSTORE_DEFAULT_COIN': settings.CCSTORE_DEFAULT_COIN,
        'CCSTORE_DEFAULT_CURRENCY': settings.CCSTORE_DEFAULT_CURRENCY
    }
