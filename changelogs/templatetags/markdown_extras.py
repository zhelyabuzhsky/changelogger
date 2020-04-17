import markdown as md
from django import template

from changelogs.models import Version

register = template.Library()


@register.filter()
def markdown(version: Version):
    version.body = version.body.replace(
        "(/uploads/", f"({version.project.url}/uploads/"
    )
    return md.markdown(version.body, extensions=["markdown.extensions.fenced_code"])
