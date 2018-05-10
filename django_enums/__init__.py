#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import, unicode_literals
import enum
from django.core import checks
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields
from logging import getLogger

__version__ = '0.1.8'


logger = getLogger(__name__)


class EnumTypedChoiceField(fields.TypedChoiceField):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: enum.Enum):
        return value.name


class EnumField(models.Field):

    def _max_length(self):
        return len(max(list(self.enum), key=(lambda x: len(x.name))).name)

    def _model_choices(self):
        return (
            (member, member.value) for member in self.enum
        )

    def _form_choices(self):
        return (
            (member.name, member.value) for member in self.enum
        )

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        self.default_enum = kwargs.get('default', None)

        if 'max_length' not in kwargs:
            kwargs['max_length'] = self._max_length()
        kwargs['choices'] = self._model_choices()

        super(EnumField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def check(self, **kwargs):
        logger.debug('call: check kwargs=%s' % kwargs)
        errors = super(EnumField, self).check(**kwargs)
        errors.extend(self._check_default_attribute(**kwargs))
        errors.extend(self._check_max_length_accommodates_enum())
        return errors

    def _check_default_attribute(self, **kwargs):
        logger.debug('call: _check_default_attribute kwargs=%s' % kwargs)
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

    def _check_max_length_accommodates_enum(self):
        if self.max_length and self.max_length < self._max_length():
            return [
                checks.Error(
                    "max_length must be equal or greater than the longest enum name",
                    obj=self,
                    id='django-enum.fields.E003',
                ),
            ]
        else:
            return []

    def from_db_value(self, value, expression, connection, context):
        logger.debug('call: from_db_value value=%s%s' % (value, type(value)))
        return self.to_python(value)

    def to_python(self, value):
        "Returns an Enum object."
        logger.debug('call: to_python value=%s%s' % (value, type(value)))
        if isinstance(value, enum.Enum) or value is None:
            logger.debug('to_python returns %s%s' % (value, type(value)))
            return value
        try:
            ret = self.enum[value]
        except KeyError:
            raise ValidationError('Could not parse value {}'.format(
                value
            ))
        logger.debug('to_python returns %s%s' % (ret, type(ret)))
        return ret

    def get_prep_value(self, value):
        logger.debug('call: get_prep_value value=%s%s' % (value, type(value)))
        if value is None:
            return value
        if not isinstance(value, self.enum):
            raise ValidationError('{} is not an instance of {}'.format(
                value, self.enum
            ))
        return value.name

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def formfield(self, **kwargs):
        # This is a fairly standard way to set up some defaults
        # while letting the caller override them.
        defaults = {
            'form_class': EnumTypedChoiceField,
            'choices_form_class': EnumTypedChoiceField,
            'choices': self._form_choices(),
            'empty_value': None,
        }
        defaults.update(kwargs)
        return super(EnumField, self).formfield(**defaults)

    def deconstruct(self):
        name, path, args, kwargs = super(EnumField, self).deconstruct()

        kwargs['enum'] = self.enum
        return name, path, args, kwargs
