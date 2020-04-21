from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_project_url(value):
    if value[-1] == "/":
        raise ValidationError(
            _("Projects's URL has slash at the end, it's not required"), params={},
        )
