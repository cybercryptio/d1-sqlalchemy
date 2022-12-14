#!/usr/bin/env python3
import grpc
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
import sqlalchemy as sa
from d1_generic import generic
from sqlalchemy.orm.session import close_all_sessions
from d1_encrypted_type import D1EncryptedType, set_client

try:
    from sqlalchemy.orm import declarative_base
except ImportError:
    # sqlalchemy 1.3
    from sqlalchemy.ext.declarative import declarative_base


uid = os.environ['D1_UID']
password = os.environ['D1_PASS']
endpoint = os.environ['D1_ENDPOINT']

Base = declarative_base()


class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(D1EncryptedType)


def main():
    # setup
    with grpc.insecure_channel(endpoint) as channel:
        client = generic.GenericClient(channel)
        client.login_user_set_token(uid, password)

        # set client
        set_client(client)

        engine = create_engine('sqlite:///:memory:')
        connection = engine.connect()

        sa.orm.configure_mappers()
        Base.metadata.create_all(connection)

        # create a configured "Session" class
        Session = sessionmaker(bind=connection)

        # create a Session
        session = Session()

        # example
        first_name = 'Michael'
        last_name = str.encode('Jackson')
        # last_name = 'Jackson'

        person = Person(first_name=first_name, last_name=last_name)
        session.add(person)
        session.commit()

        person_id = person.id

        session.expunge_all()

        person_instance = session.query(Person).get(person_id)

        print('id: {}'.format(person_instance.id))
        print('first name: {}'.format(person_instance.first_name))
        print('last name: {}'.format(person_instance.last_name))

        # teardown
        close_all_sessions()
        Base.metadata.drop_all(connection)
        connection.close()
        engine.dispose()


main()
