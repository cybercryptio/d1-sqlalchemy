#!/usr/bin/env python3
import base64

from sqlalchemy import String, TypeDecorator

UUID_LENGTH = 36

_d1client = None


def set_client(client):
    global _d1client
    _d1client = client


def get_client():
    global _d1client
    return _d1client


class D1EncryptedType(TypeDecorator):
    """
    D1EncryptedType encrypts and decrypts values on their way in and out of
    databases, respectively.
    """
    impl = String

    def __init__(
        self,
        **kwargs
    ):
        """Initialization."""
        super(D1EncryptedType, self).__init__(**kwargs)

    def process_bind_param(self, value, dialect):
        """Encrypt a value on the way in."""
        if value is not None:
            if type(value) == str:
                value = str.encode(value)
                self._underlying_type = str
            elif type(value) == bytes:
                self._underlying_type = bytes
            else:
                raise TypeError('Data type must be byte array or string.')

            response = _d1client.encrypt(value)
            return response.object_id + base64.b64encode(response.ciphertext).decode()

    def process_result_value(self, value, dialect):
        """Decrypt value on the way out."""
        if value is not None:
            object_id = value[:UUID_LENGTH]
            ciphertext = base64.b64decode(value[UUID_LENGTH:])
            decrypted_value = _d1client.decrypt(
                ciphertext, object_id)

            if self._underlying_type == str:
                return decrypted_value.plaintext.decode()
            elif self._underlying_type == bytes:
                return decrypted_value.plaintext
            else:
                raise TypeError(
                    'No in- and output data type has been recognized.')
