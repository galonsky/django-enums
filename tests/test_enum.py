#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import
from django.db import models
import os
import unittest

import django_enums
import enum


class TestEnumField(unittest.TestCase):

    def setUp(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

        import django
        django.setup()

        class MyEnum(enum.Enum):
            FOO = 'Foo'
            BAR = 'Bar'
            FOOBAR = 'FooBar'

        class MyModel(models.Model):
            enum = django_enums.EnumField(
                MyEnum,
                default=MyEnum.BAR,
            )

            class Meta:
                app_label = 'foo'

        self.enum_class = MyEnum
        self.model_class = MyModel
        self.max_length = 2
        self.tuples = [
                ('f', 'Foo'),
                ('b', 'Bar'),
                ('fb', 'FooBar'),
                ]

    def test_create_object(self):
        obj = self.model_class(enum=self.enum_class.BAR)
        assert obj.enum == self.enum_class.BAR
        errors = obj.check()
        assert len(errors) == 0

    def test_create_object_with_default(self):
        obj = self.model_class()
        assert obj.enum == self.enum_class.BAR
        errors = obj.check()
        assert len(errors) == 0

    def test_create_object_with_invalid_default(self):
        class MyModelWithInvalidDefault(models.Model):
            enum = django_enums.EnumField(
                self.enum_class,
                default='bar',
            )

            class Meta:
                app_label = 'foo'
        self.model_class = MyModelWithInvalidDefault
        obj = self.model_class()
        errors = obj.check()
        assert len(errors) == 1


if __name__ == '__main__':
    unittest.main()
