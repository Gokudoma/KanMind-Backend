import os

from django.core.wsgi import get_wsgi_application

"""
WSGI config for the core project.
Exposes the WSGI callable as a module-level variable named ``application``.
"""

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

application = get_wsgi_application()