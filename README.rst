django-enums
============

django-enums is a simple EnumField for Django models.


Installation
------------

>>> pip install django-enums


Usage
-----

Uses the native python enum.Enum class
Uses the enum `.name` for serialization and enum `.value` for display

    from django.db import models
    import enum

    class MyEnum(enum.Enum):

        FOO = 'Foo'
        BAR = 'Bar'
        FOOBAR = 'FooBar'


    class MyModel(models.Model):

        enum_field = enum.EnumField(
            MyEnum, # required
            default=MyEnum.FOO, # optional
            )
