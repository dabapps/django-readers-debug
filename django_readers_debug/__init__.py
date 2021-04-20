from django.db import models

import black
import inspect

__version__ = "0.0.3"


def safe_repr(item):
    if isinstance(item, str):
        return item
    try:
        return black.format_file_contents(repr(item), fast=False, mode=black.FileMode())
    except Exception:
        return "..."


def quote_string(string):
    return f'"{string}"'


def quote_strings_in_args(args):
    return [quote_string(arg) if isinstance(arg, str) else arg for arg in args]


def quote_strings_in_kwargs(args):
    return {
        key: quote_string(value) if isinstance(value, str) else value
        for key, value in args.items()
    }


def format_args_kwargs(args, kwargs):
    args = ", ".join(safe_repr(arg) for arg in args)
    kwargs = ", ".join(f"{key}={safe_repr(value)}" for key, value in kwargs.items())
    return ", ".join([item for item in [args, kwargs] if item])


def format_function(name, args, kwargs):
    return f"{name}({format_args_kwargs(args, kwargs)})"


def handle_pipe(fn):
    piped_fns = inspect.getclosurevars(fn).nonlocals["fns"]
    if len(piped_fns) == 1:
        return get_raw_repr(piped_fns[0])
    return format_function(
        "qs.pipe", [get_raw_repr(piped_fn) for piped_fn in piped_fns], {}
    )


def handle_include_fields(fn):
    fields = inspect.getclosurevars(fn).nonlocals["fields"]
    return format_function("qs.include_fields", quote_strings_in_args(fields), {})


def handle_auto_prefetch_relationship(fn):
    args = inspect.getclosurevars(fn).nonlocals
    kwargs = {
        "prepare_related_queryset": get_raw_repr(args["prepare_related_queryset"])
    }
    if args["to_attr"]:
        kwargs["to_attr"] = quote_string(args["to_attr"])
    return format_function(
        "qs.auto_prefetch_relationship",
        [quote_string(args["name"])],
        kwargs,
    )


def format_queryset(queryset):
    return f"{queryset.model.__name__}.objects.__(...)"


def format_prefetch_arg(arg):
    if isinstance(arg, models.Prefetch):
        kwargs = {}
        if arg.queryset:
            kwargs["queryset"] = format_queryset(arg.queryset)
        if arg.to_attr:
            kwargs["to_attr"] = quote_string(arg.to_attr)
        return format_function(
            "models.Prefetch",
            args=[quote_string(arg.prefetch_through)],
            kwargs=kwargs,
        )
    return quote_string(arg)


def handle_prefetch_related(fn):
    args = inspect.getclosurevars(fn).nonlocals["args"]
    args = [format_prefetch_arg(arg) for arg in args]
    return format_function("qs.prefetch_related", args, {})


def handle_filter_or_exclude(fn):
    vars = inspect.getclosurevars(fn).nonlocals
    name = vars["method"].__name__
    args = vars["args"]
    kwargs = quote_strings_in_kwargs(vars["kwargs"])

    args = ["models.Q(...)" for arg in args]
    return format_function(f"qs.{name}", args, kwargs)


def handle_queryset_function(fn):
    vars = inspect.getclosurevars(fn).nonlocals
    name = vars["method"].__name__
    if name == "prefetch_related":
        return handle_prefetch_related(fn)
    if name in ("filter", "exclude"):
        return handle_filter_or_exclude(fn)
    args = quote_strings_in_args(vars["args"])
    kwargs = quote_strings_in_kwargs(vars["kwargs"])
    return format_function(f"qs.{name}", args, kwargs)


def handle_annotate(fn):
    vars = inspect.getclosurevars(fn).nonlocals
    return format_function("annotate", vars["args"], vars["kwargs"])


def handle_unknown(fn):
    name = "__lambda__" if fn.__name__ == "<lambda>" else fn.__name__
    return format_function(name, [], {})


HANDLERS = {
    "pipe.<locals>.piped": handle_pipe,
    "include_fields.<locals>.fields_included": handle_include_fields,
    "auto_prefetch_relationship.<locals>.prepare": handle_auto_prefetch_relationship,
    "_method_to_function.<locals>.make_queryset_function.<locals>.queryset_function": handle_queryset_function,
    "annotate.<locals>.queryset_function": handle_annotate,
}


def get_raw_repr(fn):
    vars = inspect.getclosurevars(fn)
    if "func" in vars.nonlocals:
        fn = vars.nonlocals["func"]
    handler = HANDLERS.get(fn.__qualname__, handle_unknown)
    return handler(fn)


def get_repr(fn):
    repr = get_raw_repr(fn)
    return black.format_file_contents(repr, fast=False, mode=black.FileMode())


def debug_print(fn):
    repr = get_repr(fn)
    print(repr)
