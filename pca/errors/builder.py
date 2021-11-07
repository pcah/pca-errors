import typing as t

from pca.errors.types import (
    ExceptionWithCode,
    is_error_class,
)


def _get_cls(error: ExceptionWithCode) -> t.Type[Exception]:
    return error.__class__


def _init(error: ExceptionWithCode, *args, **kwargs) -> None:
    error.args = args
    error.kwargs = kwargs


def _getattr(error: ExceptionWithCode, name: str) -> t.Any:
    try:
        return error.kwargs[name]
    except KeyError as e:
        raise AttributeError(*e.args) from e


def _repr(error: ExceptionWithCode) -> str:
    args_str = ", ".join(repr(v) for v in error.args)
    kwargs_str = ", ".join(f"{k}={repr(v)}" for k, v in error.kwargs.items())
    repr_str = (
        f"{args_str}, {kwargs_str}" if args_str and kwargs_str else args_str or kwargs_str or ""
    )
    return f"{error.code}({repr_str})"


def _to_dict(error: ExceptionWithCode) -> t.Dict[str, t.Any]:
    return {
        "code": error.code,
        "catalog": str(error.catalog) if error.catalog else None,
        "kwargs": error.kwargs,
    }


def _clone(error: ExceptionWithCode, **kwargs) -> ExceptionWithCode:
    new_kwargs = {**error.kwargs, **kwargs}
    return error.__class__(*error.args, **new_kwargs)


def _is_conforming(error: ExceptionWithCode, error_class: t.Type[Exception]) -> bool:
    return isinstance(error, error_class)


class error_builder(type):
    """
    Error class constructed with some assumptions:
    * human-readable description of the error should be computed as late as possible (not earlier
      than on the presentation layer, where l10n & i18n process is made)
    * error instance should have a unique code
    * error instance can have an area which describes its general topic
    * error instances can be gathered into catalogs which describe their common reason or a place
      to be raised
    * an error instance is a value object, defined by their code and area
    * an error can have params, which can be used to pass some data specific for the place
      the instance is raised, but isn't considered a part of the value for checking instance
      equality
    * error can have a `hint`, only for the purpose of giving developer a hint, what this
      error class is made for.
    """

    def __new__(
        mcs,
        name: str = "",
        bases: t.Union[t.Type[Exception], t.Sequence[t.Type[Exception]]] = Exception,
        hint: str = "",
    ):
        if is_error_class(bases):
            bases = (bases,)
        namespace = {
            "code": name,
            "cls": property(_get_cls),
            "hint": hint,
            "catalog": None,
            "kwargs": None,
            "__init__": _init,
            "__getattr__": _getattr,
            "__repr__": _repr,
            "to_dict": _to_dict,
            "clone": _clone,
            "is_conforming": _is_conforming,
        }
        return super().__new__(mcs, name, bases, namespace)

    def __init__(cls, *args, **kwargs):
        pass

    def __repr__(cls) -> str:

        catalog_str = f" catalog={str(cls.catalog)}" if cls.catalog else ""
        return f"<{cls.code}{catalog_str}>"

    __str__ = __repr__

    def __set_name__(cls, owner: t.Any, name: str) -> None:
        """
        Setting an instance on an ErrorCatalog subclass as a filed closely bounds both
        and can set value to its name.
        """
        from .catalog import ErrorCatalog

        if not issubclass(owner, ErrorCatalog):
            return
        cls.catalog = owner
        name = cls.code or name
        cls.code = cls.__name__ = name

    def conforms(cls, error: Exception) -> bool:
        return isinstance(error, cls)
