#!/usr/bin/env python3
import grpc
import os

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
import sqlalchemy as sa
from d1_generic import generic
from sqlalchemy.orm.session import close_all_sessions
from d1_encrypted_type import D1EncryptedType, set_access_token, set_client

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
    last_name = Column(D1EncryptedType(String))


def main():
    # setup
    with grpc.insecure_channel(endpoint) as channel:
        client = generic.GenericClient(channel)
        response = client.login_user(uid, password)

        # set client and access token
        set_client(client)
        set_access_token(response.access_token)

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
        last_name = bytes('Jackson', 'utf-8')

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
