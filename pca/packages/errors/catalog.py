import typing as t

from collections import OrderedDict

from .types import (
    ExceptionWithCodeType,
    is_error_class,
)


class ErrorCatalogMeta(type):

    __error_registry: t.Dict[str, ExceptionWithCodeType]
    __subcatalog_registry: t.Dict[str, "ErrorCatalogMeta"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__error_registry = OrderedDict(
            (v.code, v) for _, v in self.__dict__.items() if is_error_class(v)
        )
        self.__subcatalog_registry = OrderedDict(
            (v.__name__, v) for _, v in self.__dict__.items() if isinstance(v, ErrorCatalogMeta)
        )

    def __str__(self) -> str:
        return self.__name__

    def __repr__(self) -> str:
        return f"{self.__module__}.{self.__qualname__}"

    def __iter__(self) -> t.Iterator[ExceptionWithCodeType]:
        """Iterate over registered errors."""
        yield from self.__error_registry.values()
        yield from (e for c in self.__subcatalog_registry.values() for e in c)

    def __len__(self) -> int:
        return len(self.all())

    def __contains__(self, item: ExceptionWithCodeType) -> bool:
        return item in self.all()

    def add_instance(self, error_class: ExceptionWithCodeType) -> None:
        """Registers an ExceptionWithCode subtype as an element of the ErrorCatalog."""
        self.__error_registry[error_class.code] = error_class
        setattr(self, error_class.code, error_class)
        error_class.catalog = t.cast("ErrorCatalog", self)

    def all(self) -> t.Tuple[ExceptionWithCodeType, ...]:
        return tuple(self.__iter__())

    def subcatalogs(self) -> t.Tuple["ErrorCatalogMeta", ...]:
        return tuple(self.__subcatalog_registry.values())


class ErrorCatalog(metaclass=ErrorCatalogMeta):
    """
    A class that can serve as a collection of named BaseErrors, gathered with a common reason.
    Instances of BaseErrors are meant to be declared as fields. Names of their fields may be
    used as default value of `code` for each instance.

    >>> class SomeCatalog(ErrorCatalog):
    ...     SomeError = error_builder()
    ...     AnotherError = error_builder("ExpliciteNameForAnotherError")


    Developers are encouraged to gather errors of their business logic into such error classes.
    Such catalogs can be nested to structurize their relation further, in a form of a tree.

    >>> class ExternalCatalog(ErrorCatalog):
    ...     ExternalError = error_builder()

    >>> class CompositeCatalog(ErrorCatalog):
    ...     OwnError = error_builder()
    ...     ExternalCatalogIncluded = ExternalCatalog
    ...
    ...     class NestedCatalog(ErrorCatalog):
    ...         NestedError = error_builder()

    >>> assert CompositeCatalog.all() == (
    ...     CompositeCatalog.OwnError,
    ...     ExternalCatalog.ExternalError,
    ...     CompositeCatalog.NestedCatalog.NestedError
    ... )


    If you want to reuse an error already attached to a catalog, use error's `clone` method
    like this:

    >>> class OldCatalog(ErrorCatalog):
    ...     OldError = error_builder()

    >>> class NewCatalog(ErrorCatalog):
    ...     AnExistingError = OldCatalog.OldError.clone()

    >>> assert OldCatalog.OldCatalog is not NewCatalog.AnExistingError
    >>> assert OldCatalog.OldCatalog.catalog == OldCatalog
    >>> assert NewCatalog.AnExistingError.catalog == NewCatalog
    """
