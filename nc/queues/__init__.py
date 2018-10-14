from allauth.utils import import_attribute

from django.conf import settings


def get_queue_backend():
    """
    Returns instance queue backend that is active in the project.
    """
    return import_attribute(settings.QUEUE_BACKEND)()
