import typing as t


if t.TYPE_CHECKING:
    from .catalog import ErrorCatalog

DictStrAny = t.Dict[str, t.Any]


class ExceptionWithCode(Exception):
    code: str
    cls: t.Type[Exception]
    hint: str
    catalog: "ErrorCatalog"
    args: tuple
    kwargs: DictStrAny

    def to_dict(self) -> DictStrAny:
        "Returns serializable form."

    def clone(self) -> "ExceptionWithCode":
        "Duplicates the `self` instance, updating its `kwargs` iff such update is defined."
