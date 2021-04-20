django-readers-debug
====================

**STATUS: EXPERIMENTAL**

**A pretty-printer for debugging [django-readers](https://github.com/dabapps/django-readers) queryset functions.**

### Installation

Install from PyPI

    pip install django-readers-debug

## Usage

Without `django-readers-debug`:

```pycon
>>> from django_readers import qs
>>> prepare = qs.pipe(
... qs.include_fields("name"),
... qs.auto_prefetch_relationship("author", qs.include_fields("name")),
... qs.filter(publication_year__gte=2021),
... )
>>> print(prepare)
<function pipe.<locals>.piped at 0x10ce2a670>
>>>
```

With `django-readers-debug`:

```pycon
>>> from django_readers_debug import debug_print
>>> debug_print(prepare)
qs.pipe(
    qs.include_fields("name"),
    qs.auto_prefetch_relationship(
        "author", prepare_related_queryset=qs.include_fields("name")
    ),
    qs.filter(publication_year__gte=2021),
)
```

## Known limitations

Best-effort printing of `Q` objects and `Prefetch` objects only.

## Code of conduct

For guidelines regarding the code of conduct when contributing to this repository please review [https://www.dabapps.com/open-source/code-of-conduct/](https://www.dabapps.com/open-source/code-of-conduct/)
