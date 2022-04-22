import typing as t

from collections import OrderedDict

from .types import (
    ExceptionWithCodeType,
    is_error_class,
)


class ErrorCatalogMeta(type):

    _errors: t.Dict[str, ExceptionWithCodeType]
    _own_nested_catalogs: t.Dict[str, "ErrorCatalogMeta"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._errors = OrderedDict(
            (v.code, v) for _, v in self.__dict__.items() if is_error_class(v)
        )
        self._own_nested_catalogs = OrderedDict(
            (v.__name__, v) for _, v in self.__dict__.items() if isinstance(v, ErrorCatalogMeta)
        )

    def __str__(self) -> str:
        return self.__name__

    def __repr__(self) -> str:
        return f"{self.__module__}.{self.__qualname__}"

    def __iter__(self) -> t.Iterator[ExceptionWithCodeType]:
        """
        Iterate over errors, including inheritance, and then, iterate over nested catalogs
        (which might include its own nested catalogs). Supports field overriding by inheritance.
        """
        yield from self._not_nested_errors.values()
        yield from (e for c in self._nested_catalogs.values() for e in c)

    @property
    def _super_catalogs(self) -> t.Iterable["ErrorCatalogMeta"]:
        """
        Tuple of ErrorCatalog proper subclasses that this catalog inherits from,
        INCLUDING the former catalog itself.

        NB: The order is reversed comparing to the Pythonic MRO, ie. the class itself
        is the LAST one.
        """
        return reversed(
            list(c for c in self.__mro__ if isinstance(c, ErrorCatalogMeta) and c != ErrorCatalog)
        )

    @property
    def _not_nested_errors(self) -> t.Dict[str, ExceptionWithCodeType]:
        """
        Dict of errors NOT in nested catalogs. Supports field overriding by inheritance.
        """
        return {
            name: error_class
            for catalog in self._super_catalogs
            for name, error_class in catalog._errors.items()
        }

    @property
    def _nested_catalogs(self) -> t.Dict[str, "ErrorCatalogMeta"]:
        """
        Dict of nested catalogs. Supports field overriding by inheritance.
        """
        return {
            name: nested
            for catalog in self._super_catalogs
            for name, nested in catalog._own_nested_catalogs.items()
        }

    @property
    def all(self) -> t.Tuple[ExceptionWithCodeType, ...]:
        """
        A tuple containing all the errors defined in the catalog, including nesting & inheritance.
        """
        return tuple(self.__iter__())

    def __len__(self) -> int:
        return len(self.all)

    def __contains__(self, item: ExceptionWithCodeType) -> bool:
        return item in self.all

    def add_instance(self, error_class: ExceptionWithCodeType) -> None:
        """Registers an ExceptionWithCode subtype as an element of the ErrorCatalog."""
        self._errors[error_class.code] = error_class
        setattr(self, error_class.code, error_class)
        error_class.catalog = t.cast("ErrorCatalog", self)


class ErrorCatalog(metaclass=ErrorCatalogMeta):
    """
    A class that can serve as a collection of named exception classes, gathered with a common
    reason. [...]

    Exception classes are meant to be declared as fields. Names of the fields may be
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
