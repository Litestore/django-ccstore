from channels import Group
from channels.auth import channel_session_user_from_http


@channel_session_user_from_http
def ws_connect(message):
    Group('ticker').add(message.reply_channel)
    message.reply_channel.send({"accept": True})


@channel_session_user_from_http
def ws_disconnect(message):
    Group('ticker').discard(message.reply_channel)
