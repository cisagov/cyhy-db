import ipaddress
from mongoengine.base.fields import BaseField


class IPAddressField(BaseField):
    def validate(self, value):
        if not isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            self.error(f'Value "{value}" is not a valid IP address.')

    def to_mongo(self, value):
        if value is None:
            return value
        if isinstance(value, (ipaddress.IPv4Address, ipaddress.IPv6Address)):
            return str(value)
        self.error(f'Value "{value}" cannot be converted to a string IP address.')

    def prepare_query_value(self, op, value):
        return super().prepare_query_value(op, self.to_mongo(value))

    @staticmethod
    def _parse_ip(value):
        if isinstance(value, str):
            return ipaddress.ip_address(value.strip())
        return value

    def to_python(self, value):
        try:
            return self._parse_ip(value)
        except ValueError as e:
            self.error(f'Value "{value}" is not a valid IP address.')
