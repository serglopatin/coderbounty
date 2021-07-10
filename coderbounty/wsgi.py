import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "coderbounty.settings")

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

application = get_wsgi_application()
application = WhiteNoise(application)