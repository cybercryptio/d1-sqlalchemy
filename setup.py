from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='d1_sqlalchemy',
    description='A Python ORM integration',
    license="Apache License, Version 2.0",
    long_description=long_description,
    url="https://github.com/cybercryptio/d1-sqlalchemy",
)
