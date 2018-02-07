import cryptocompare
import json

from celery import shared_task
from channels import Group
from django.conf import settings
from django.core.cache import cache


@shared_task
def update_ticker():
    prices = cryptocompare.get_price(
        settings.CCSTORE_TICKER_COINS,
        settings.CCSTORE_TICKER_CURRENCIES
    )
    cache.set('ticker', prices)
    Group('ticker').send({
        "text": json.dumps({
            'msg_type': 'ticker',
            'ticker': prices
        })
    })
    return prices
