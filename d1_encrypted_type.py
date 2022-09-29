#!/usr/bin/env python3
import base64
import datetime
import json

from sqlalchemy_utils.types.encrypted.encrypted_type import DatetimeHandler
from sqlalchemy import String, TypeDecorator
from sqlalchemy_utils.types.json import JSONType
from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible

UUID_LENGTH = 36


class D1EncryptedType(TypeDecorator, ScalarCoercible):
    """
    D1EncryptedType encrypts and decrypts values in their way in and out of
    databases, respectively.
    """
    impl = String
    cache_ok = True

    def __init__(
        self,
        client,
        access_token=None,
        type_in=None,
        **kwargs
    ):
        """Initialization."""
        super(D1EncryptedType, self).__init__(**kwargs)
        # set the underlying type
        if type_in is None:
            type_in = String()
        elif isinstance(type_in, type):
            type_in = type_in()
        self.underlying_type = type_in
        self.access_token = access_token
        self.client = client

    def process_bind_param(self, value, dialect):
        """Encrypt a value on the way in."""
        if value is not None:

            try:
                value = self.underlying_type.process_bind_param(
                    value, dialect
                )

            except AttributeError:
                # Doesn't have 'process_bind_param'

                # Handle 'boolean' and 'dates'
                type_ = self.underlying_type.python_type
                if issubclass(type_, bool):
                    value = 'true' if value else 'false'

                elif issubclass(type_, (datetime.date, datetime.time)):
                    value = value.isoformat()

                elif issubclass(type_, JSONType):
                    value = json.dumps(value)

            response = self.client.encrypt(value, self.access_token)
            return response.object_id + base64.b64encode(response.ciphertext).decode()

    def process_result_value(self, value, dialect):
        """Decrypt value on the way out."""
        if value is not None:
            object_id = value[:UUID_LENGTH]
            ciphertext = base64.b64decode(value[UUID_LENGTH:])
            decrypted_value = self.client.decrypt(
                ciphertext, object_id, self.access_token)

            try:
                return self.underlying_type.process_result_value(
                    decrypted_value, dialect
                )

            except AttributeError:
                # Doesn't have 'process_result_value'

                # Handle 'boolean' and 'dates'
                type_ = self.underlying_type.python_type
                date_types = [datetime.datetime, datetime.time, datetime.date]

                if issubclass(type_, bool):
                    return decrypted_value == 'true'

                elif type_ in date_types:
                    return DatetimeHandler.process_value(
                        decrypted_value, type_
                    )

                elif issubclass(type_, JSONType):
                    return json.loads(decrypted_value)

                # Handle all others
                return self.underlying_type.python_type(decrypted_value)

    def _coerce(self, value):
        if isinstance(self.underlying_type, ScalarCoercible):
            return self.underlying_type._coerce(value)

        return value
