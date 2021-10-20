import typing as t

from collections import OrderedDict

from .builder import ErrorBuilder


class ErrorCatalogMeta(type):

    _registry: t.Dict[str, ErrorBuilder]

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._registry = OrderedDict(
            (v.code, v) for k, v in cls.__dict__.items() if isinstance(v, ErrorBuilder)
        )

    def __str__(cls) -> str:
        return f"{cls.__name__}"

    def __repr__(cls) -> str:
        return f"{cls.__module__}.{cls.__qualname__}"

    def __iter__(cls) -> ErrorBuilder:
        """Iterate over registered errors."""
        yield from cls._registry.values()

    def __len__(cls) -> int:
        return len(cls._registry)

    def __contains__(cls, item: ErrorBuilder) -> bool:
        return item in cls._registry.values()

    def add_instance(cls, error: ErrorBuilder) -> None:
        """Registers an instance of an BaseError as an element of the ErrorCatalog."""
        cls._registry[error.code] = error
        setattr(cls, error.code, error)
        error.__dict__["catalog"] = cls

    def all(cls) -> t.Tuple[ErrorBuilder]:
        return tuple(cls._registry.values())


class ErrorCatalog(metaclass=ErrorCatalogMeta):
    """
    A class that can serve as a collection of named BaseErrors, gathered with a common reason.
    Instances of BaseErrors are meant to be declared as fields. Names of their fields may be
    used as default value of `code` for each instance. The catalog may set default value of
    `area` for all of them.

    Developers are encouraged to gather errors of their business logic into such error classes.
    If you want to reuse an error already attached to a catalog, use error's `clone` method
    like this:

    >>> class OldCatalog(ErrorCatalog):
    ...     ERROR = ExceptionWithCode()

    >>> class NewCatalog(ErrorCatalog):
    ...     AN_EXISTING_ERROR = OldCatalog.ERROR.clone()

    >>> assert OldCatalog.ERROR == NewCatalog.AN_EXISTING_ERROR
    >>> assert OldCatalog.ERROR.catalog == OldCatalog
    >>> assert NewCatalog.AN_EXISTING_ERROR.catalog == NewCatalog
    """
