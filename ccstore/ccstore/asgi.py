import os
from channels.asgi import get_channel_layer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ccstore.settings")
channel_layer = get_channel_layer()
