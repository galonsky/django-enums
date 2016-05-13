#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import
from django.db import models
from enum import Enum as BaseEnum
from itertools import ifilter
from logging import getLogger
import django


logger = getLogger(__name__)

class Enum(BaseEnum):

    def __init__(self, key, label):
        self.key = key
        self.label = label

    @classmethod
    def get_by_key(cls, key):
        return next(iter(filter(lambda x: x.key == key, list(cls))), None)

    @classmethod
    def tuples(cls):
        return map(lambda x: x.value, list(cls))

    @classmethod
    def choices(cls):
        return cls.tuples()

    @classmethod
    def get_max_length(cls):
        return len(max(list(cls), key=(lambda x: len(x.key))).key)


class EnumField(models.CharField):

    __metaclass__ = models.SubfieldBase

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        self.default_enum = kwargs.pop('default', None)
        kwargs['max_length'] = self.enum.get_max_length()
        kwargs['choices'] = self.enum.choices()
        if isinstance(self.default_enum, self.enum):
            kwargs['default'] = self.default_enum.key
        super(EnumField, self).__init__(*args, **kwargs)

    def check(self, **kwargs):
        errors = super(EnumField, self).check(**kwargs)
        errors.extend(self._check_enum_attribute(**kwargs))
        errors.extend(self._check_default_attribute(**kwargs))
        return errors

    def _check_enum_attribute(self, **kwargs):
        if self.enum is None:
            return [
                    checks.Error(
                            "EnumFields must define a 'enum' attribute.",
                            obj=self,
                            id='django-enum.fields.E001',
                            ),
                    ]
        else:
            return []

    def _check_default_attribute(self, **kwargs):
        if self.default_enum is not None:
            if not isinstance(self.default_enum, self.enum):
                return [
                        checks.Error(
                                "'default' must be a member of %s." % (self.enum.__name__),
                                obj=self,
                                id='django-enum.fields.E002',
                                ),
                        ]
        return []

    def from_db_value(self, value, expression, connection, context):
        logger.debug('call: from_db_value value=%s%s' % (value, type(value)))
        if value is None:
            logger.debug('from_db_value returns %s%s' % (value, type(value)))
            return value
        logger.debug('from_db_value returns %s%s' % (self.enum.get_by_key(value), type(value)))
        return self.enum.get_by_key(value)

    def to_python(self, value):
        logger.debug('call: to_python value=%s%s' % (value, type(value)))
        if isinstance(value, Enum) or value is None:
            logger.debug('to_python returns %s%s' % (value, type(value)))
            return value
        logger.debug('to_python returns %s%s' % (self.enum.get_by_key(value), type(value)))
        return self.enum.get_by_key(value)

    def db_type(self, connection):
        logger.debug('db_type returns char(%s)' % self.max_length)
        return 'char(%s)' % self.max_length

    def get_prep_value(self, value):
        logger.debug('call: get_prep_value value=%s%s' % (value, type(value)))
        if isinstance(value, Enum):
            logger.debug('get_prep_value returns %s%s' % (value.key, type(value)))
            return value.key
        logger.debug('get_prep_value returns %s%s' % (value, type(value)))
        return value

    def value_to_string(self, obj):
        logger.debug('call: value_to_string obj=%s' % obj)
        value = self.value_from_object(obj)
        return self.get_prep_value(value)

    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()
        if django.VERSION >= (1, 9):
            kwargs['enum'] = self.enum
        else:
            path = 'django.db.models.fields.CharField'
        return name, path, args, kwargs
