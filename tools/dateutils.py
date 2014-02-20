import datetime
from pytz import timezone, utc

gmt = timezone('GMT')


def current_datetime():
    """ Returns a GMT datetime object """
    return datetime.datetime.utcnow().replace(tzinfo=gmt)


def offset_current_datetime(offset):
    """ Returns a GMT datetime object offset by the given offset """
    return current_datetime() + datetime.timedelta(**offset)


def offset_token_current_datetime():
    """ Returns the offset for the TOKEN EXPIRATION to use in the auth.models.Token Model """
    token_expiration = {'hours': 12}
    return offset_current_datetime(token_expiration)
