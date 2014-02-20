from bulbs.property import *
from tools.bulbs_extra_fields_validators import validate_email, validate_ipv4_address, URLValidator, ValidationError
from pytz import timezone

gmt = timezone('GMT')


class Email(String):
    """ Represents an email type attribute

    """

    @classmethod
    def get_domain(cls, value):
        value = unicode(value)
        assert u'@' in value, "Missing domain suffix"
        domain = value.split(u'@', 1)[-1]
        assert u'@' not in domain, "Too many domains given"
        return domain

    def validate(self, key, value):
        # perform type validation of String
        super(Email, self).validate(key, value)
        # now check that it is a valid email
        ## utilize django validator methods
        validate_email(value)


class IPV4Address(String):
    """ Represents and IPV4 string

    """

    def validate(self, key, value):
        # perform type validation of String
        super(IPV4Address, self).validate(key, value)
        # now check that it is a valid IPV4 address
        ## utilize django validator methods
        validate_ipv4_address(value)


class URL(String):
    """ Represents a URL

    """

    def validate(self, key, value):
        # perform type validation of String
        super(URL, self).validate(key, value)
        # now check that it is a valid URL
        ## utilize django validator methods
        URLValidator(value)


class PositiveInteger(Integer):
    """ Represents a positive Integer
    """

    def validate(self, key, value):
        # perform the type validation of the standard Integer
        super(PositiveInteger, self).validate(key, value)
        # now check that it is positive
        if value < 0:
            raise ValidationError("Value must be a Positive Integer")


class DateTimeGMT(DateTime):

    def _coerce(self, value):
        dt = super(DateTimeGMT, self)._coerce(value)

        if dt.tzinfo is not None:
            dt = dt.astimezone(tz=gmt)
        else:
            dt = dt.replace(tzinfo=gmt)

        return dt

    def to_python(self, type_system, value):
        dt = super(DateTimeGMT, self).to_python(type_system, value)

        dt = dt.replace(tzinfo=gmt)

        return dt