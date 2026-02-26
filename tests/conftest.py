from django.conf import settings

import django

if not settings.configured:
    settings.configure(
        SECRET_KEY="django-readers-debug-tests",
        INSTALLED_APPS=["django.contrib.contenttypes"],
        DATABASES={
            "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}
        },
        USE_TZ=True,
    )

    django.setup()
