# CYBERCRYPT D1 SQLAlchemy

This integration can be used to encrypt and decrypt data transparently when reading and writing to the database, using [CYBERCRYPT D1 Generic](https://github.com/cybercryptio/d1-service-generic/). The data is encrypted in the application layer in such a way that the database itself never receives the data in plain text.

This protects the data in the database from being read by third parties and tampering.

The integration tool [SQLAlchemy](https://sqlalchemy.org) has been used.

## Supported databases
The supported databases are:

* SQLite
* Postgresql
* MySQL
* Oracle
* MS-SQL
* Firebird
* Sybase


## Usage
When creating a table, the data type `D1EncryptedType` can be assigned to a column which will ensure that the data in that column is encrypted and decrypted on the way in and out of the database, respectively. In the example below, the column `last_name` in the table `person` will be encrypted before being stored in the database:

```python
class Person(Base):
    __tablename__ = "person"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(D1EncryptedType)
```


## Limitations

- Currently only byte array and string data fields can be encrypted.
- Encrypted data is not searchable by the database.

## License

The software in the CYBERCRYPT d1-sqlalchemy repository is licensed under the Apache License 2.0.
