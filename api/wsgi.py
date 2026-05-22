import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
app = application

_vercel_initialized = False
if os.environ.get("VERCEL") and not _vercel_initialized:
    try:
        from django.core.management import call_command

        call_command("migrate", "--noinput")
        _vercel_initialized = True
    except Exception:
        pass
