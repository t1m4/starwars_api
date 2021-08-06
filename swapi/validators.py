from django.core.exceptions import ValidationError


def validate_positive(value):
    if value < 1:
        raise ValidationError(('%(value) is not an positive number'), params={'value': value}, )
    return value
