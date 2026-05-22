import os

import django


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    django.setup()
    from django.core.management import call_command

    call_command("migrate", "--noinput")


if __name__ == "__main__":
    main()
