import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

if os.environ.get("VERCEL"):
    from django.core.management import call_command

    call_command("migrate", "--noinput")
    call_command("collectstatic", "--noinput")
