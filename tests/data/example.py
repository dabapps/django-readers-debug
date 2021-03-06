from django.db.models import Count, F, Func, IntegerField, Prefetch, Q, Sum
from django.db.models.query import ModelIterable
from django_readers import qs


class User:
    """
    Quacks just enough like a Django model for the tests to work
    """

    class Manager:
        def all(self):
            return self

        def only(self, _):
            return self

        class query:
            deferred_loading = [[]]

        class _iterable_class(ModelIterable):
            pass

        class User:
            pass

        model = User

    objects = Manager()


def some_queryset_function(queryset):
    return queryset


class SomeClass:
    def some_queryset_function(self, queryset):
        return queryset


class CustomFunction(Func):
    def __repr__(self):
        return "some nonsense"


prepare = qs.pipe(
    qs.include_fields("title"),
    qs.auto_prefetch_relationship("author", qs.include_fields("name")),
    qs.filter(publication_year__gte=2021),
    qs.filter(Q(type="HARDBACK")),
    qs.filter(title__startswith="Space"),
    qs.exclude(Q(type="MAGAZINE")),
    qs.select_related("info"),
    qs.select_related_fields("info__name"),
    qs.order_by("name"),
    qs.distinct(),
    qs.prefetch_related(Prefetch("collections")),
    qs.prefetch_related(
        Prefetch("owner", queryset=User.objects.all(), to_attr="owner")
    ),
    qs.prefetch_forward_relationship(
        "co_author", User.objects.all(), qs.include_fields("name"), to_attr="coauthor"
    ),
    qs.prefetch_reverse_relationship(
        "publisher", "published_by", User.objects.all(), qs.include_fields("name")
    ),
    qs.prefetch_many_to_many_relationship(
        "collaborators", User.objects.all(), qs.include_fields("name")
    ),
    some_queryset_function,
    SomeClass().some_queryset_function,
    lambda queryset: queryset,
    qs.annotate(Count("page")),
    qs.annotate(num_pages=Count("page")),
    qs.annotate(
        total_pages=Sum(
            F("intro_pages") + F("other_pages"),
            output_field=IntegerField(),
        ),
    ),
    qs.annotate(title_upper=Func(F("title"), function="UPPER")),
    qs.annotate(CustomFunction(), custom=CustomFunction()),
)
