import typing as t

from collections import OrderedDict

from .types import (
    ExceptionWithCodeType,
    is_error_class,
)


class ErrorCatalogMeta(type):

    _registry: t.Dict[str, ExceptionWithCodeType]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._registry = OrderedDict(
            (v.code, v) for _, v in self.__dict__.items() if is_error_class(v)
        )

    def __str__(self) -> str:
        return self.__name__

    def __repr__(self) -> str:
        return f"{self.__module__}.{self.__qualname__}"

    def __iter__(self) -> t.Iterator[ExceptionWithCodeType]:
        """Iterate over registered errors."""
        yield from self._registry.values()

    def __len__(self) -> int:
        return len(self._registry)

    def __contains__(self, item: ExceptionWithCodeType) -> bool:
        return item in self._registry.values()

    def add_instance(self, error_class: ExceptionWithCodeType) -> None:
        """Registers an ExceptionWithCode subtype as an element of the ErrorCatalog."""
        self._registry[error_class.code] = error_class
        setattr(self, error_class.code, error_class)
        error_class.catalog = t.cast("ErrorCatalog", self)

    def all(self) -> t.Tuple[ExceptionWithCodeType, ...]:
        return tuple(self._registry.values())


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
