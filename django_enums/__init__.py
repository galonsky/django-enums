#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

from __future__ import division, print_function, absolute_import, unicode_literals
import enum

import six
from django.core import checks
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import fields


class EnumTypedChoiceField(fields.TypedChoiceField):
    """
    A TypedChoiceField that serializes an enum member to its name
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: enum.Enum):
        """
        This is called when creating the form. Returning the enum name here
        to be consistent with our name-keyed tuples in the form `choices`
        """
        return value.name


class EnumField(models.Field):
    """
    Database field represented by a Python enum.
    Set and get the attribute as the enum member itself.

    Serialized to the database as a CharField (varchar), using the enum name
    as the value

    Uses the enum members to determine both the `choices` for the field

    This is purposefully not a subclass of CharField since CharField
    adds validation on max_length that doesn't quite work with enums
    """

    def _max_length(self):
        """
        :return: the length of the longest name of this enum class
        """
        return len(max(list(self.enum), key=(lambda x: len(x.name))).name)

    def _model_choices(self):
        """
        Returns tuples of (member, member.value) for model validation.
        Uses the member as the key since the member is what will be on the model
        """
        return (
            (member, member.value) for member in self.enum
        )

    def _form_choices(self):
        """
        Returns tuples of (name, value) for form construction/validation.
        Using the enum name since that's what we want forms to use
        """
        return (
            (member.name, member.value) for member in self.enum
        )

    def __init__(self, enum, *args, **kwargs):
        self.enum = enum
        self.default_enum = kwargs.get('default', None)

        kwargs['choices'] = self._model_choices()

        super(EnumField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        """
        For database/migration level decisions, this is a Charfield
        """
        return "CharField"

    def check(self, **kwargs):
        errors = super(EnumField, self).check(**kwargs)
        errors.extend(self._check_default_attribute(**kwargs))
        errors.extend(self._check_max_length_attribute(**kwargs))
        errors.extend(self._check_max_length_accommodates_enum())
        return errors

    # This is lifted from CharField
    def _check_max_length_attribute(self, **kwargs):
        if self.max_length is None:
            return [
                checks.Error(
                    "CharFields must define a 'max_length' attribute.",
                    obj=self,
                    id='fields.E120',
                )
            ]
        elif not isinstance(self.max_length, six.integer_types) or self.max_length <= 0:
            return [
                checks.Error(
                    "'max_length' must be a positive integer.",
                    obj=self,
                    id='fields.E121',
                )
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
        return self.to_python(value)

    def to_python(self, value):
        """
        This is called after grabbing the value from the db.
        Per django docs, this needs to support both strings and the enum value
        """
        if isinstance(value, enum.Enum) or value is None:
            return value
        try:
            ret = self.enum[value]
        except KeyError:
            raise ValidationError('Could not parse value {}'.format(
                value
            ))
        return ret

    def get_prep_value(self, value):
        """
        This is called to serialize the value for use in queries
        """
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
        """
        Initializes a EnumTypedChoiceField with our form choices
        """
        defaults = {
            'form_class': EnumTypedChoiceField,
            'choices_form_class': EnumTypedChoiceField,
            'choices': self._form_choices(),
            'empty_value': None,
        }
        defaults.update(kwargs)
        return super(EnumField, self).formfield(**defaults)

    def deconstruct(self):
        """
        This is called to serialize the state of the field for migration
        purposes. Retains all the kwargs, and adds enum
        """
        name, path, args, kwargs = super(EnumField, self).deconstruct()

        kwargs['enum'] = self.enum
        return name, path, args, kwargs
