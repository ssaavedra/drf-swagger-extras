"""Django REST Framework Decorators for Swagger

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

try:
    from pypandoc import convert

    def read_md(f):
        return convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Markdown to reStructuredText")
    def read_md(f):
        with open(f, 'r', encoding='utf-8') as fh:
            text = fh.read()
        return text

here = path.abspath(path.dirname(__file__))


setup(
    name='drf-swagger-extras',
    version='0.1.0.dev1',
    description='Django REST Framework extras for better Swagger/OpenAPI self-documentation',
    long_description=read_md('README.md'),
    url='https://github.com/ssaavedra/drf-swagger-extras',
    author='Santiago Saavedra',
    author_email='ssaavedra@gpul.org',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
    # keywords='',
    packages=['drf_swagger_extras'],
    install_requires=['djangorestframework~=3.4', 'coreapi~=1.32.0', 'openapi-codec~=1.0'],
    extras_require={
        'dev': ['pypandoc~=1.2'],
        'test': ['coverage~=4.2', 'pytest~=3.0.2', 'tox~=2.3'],
    },
)
