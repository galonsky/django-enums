django-enums
============

django-enums is a simple Enum class and EnumField for Django models.
Enum class inherits Enum class in the default enum module.
EnumFiled class inherits Charfield.

Installation
------------

>>> pip install django-enums


Usage
-----

Inherit Enum class and set it to EnumField.enum.::

    from django.db import models
    from django_enums import enum

    class MyEnum(enum.Enum):

        __order__ = 'FOO BAR FOOBAR' # for python 2

        FOO = ('f', 'Foo')
        BAR = ('b', 'Bar')
        FOOBAR = ('fb', 'FooBar')


    class MyModel(models.Model):

        enum_field = enum.EnumField(
            MyEnum, # required
            default=MyEnum.FOO, # optional
            )
