import decimal
from django.core.cache import cache
from django.conf import settings

from cc.models import Currency


def get_default_currency():
    try:
        currency = Currency.objects.get(ticker=settings.CCSTORE_DEFAULT_COIN)
    except Currency.DoesNotExist:
        return
    return currency


def get_crypto_price(currency=settings.CCSTORE_DEFAULT_CURRENCY,
                     ticker=settings.CCSTORE_DEFAULT_COIN):
    prices = cache.get('ticker')
    if not prices:
        raise RuntimeError('Run apps.core.tasks.update_ticker task first.')
    return prices[ticker][currency]


def crypto_to_fiat(amount, currency=settings.CCSTORE_DEFAULT_CURRENCY,
                   ticker=settings.CCSTORE_DEFAULT_COIN, price=None):
    if not isinstance(amount, decimal.Decimal):
        amount = decimal.Decimal(amount)
    if not price:
        price = get_crypto_price(currency, ticker)
    result = amount * decimal.Decimal(price)
    return decimal.Decimal("{:.2f}".format(result))


def fiat_to_crypto(amount, currency=settings.CCSTORE_DEFAULT_CURRENCY,
                   ticker=settings.CCSTORE_DEFAULT_COIN, price=None):
    if not isinstance(amount, decimal.Decimal):
        amount = decimal.Decimal(amount)
    coin_price = crypto_to_fiat(1, currency=currency, ticker=ticker, price=price)
    result = amount / decimal.Decimal(coin_price)
    return decimal.Decimal("{:.8f}".format(result))


def to_satoshi(amount):
    return int(amount * 10**9)


def from_satoshi(satoshi):
    result = satoshi / 10**9
    return decimal.Decimal("{:.8f}".format(result))


def calculate_fee(fee, total):
    fee = (total * fee) / 100
    return fee.quantize(decimal.Decimal(10) ** -2)
