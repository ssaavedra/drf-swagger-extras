"""Django REST Framework Decorators for Swagger

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='drf-swagger-extras',
    version='0.1.0.dev1',
    description='Django REST Framework extras for better Swagger/OpenAPI self-documentation',
    long_description=long_description,
    url='https://github.com/ssaavedra/drf-swagger-extras',
    author='Santiago Saavedra',
    author_email='ssaavedra@gpul.org',
    license='MIT',
    classifiers=[

    ],
    keywords='',
    packages=['drf_openapi'],
    install_requires=['rest_framework~=3.4', 'coreapi~=1.32', 'openapi-codec~=1.0'],
    extras_require={
        'test': ['coverage'],
    },
)
