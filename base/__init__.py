# __init__.py (same level as settings.py)
from .celery import app as celery_app

__all__ = ['celery_app']
