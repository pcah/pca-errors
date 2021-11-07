import typing as t

from dataclasses import dataclass
from types import TracebackType


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

    def is_conforming(self, error_class: t.Type[Exception]) -> bool:
        "Checks iff the instance conforms error type `error_class`."


@dataclass(frozen=True)
class ExceptionInfo:
    type: t.Type[BaseException]
    value: BaseException
    traceback: TracebackType


def is_error_class(sth: t.Any) -> bool:
    return isinstance(sth, type) and issubclass(sth, Exception)


ExceptionTypeOrTypes = t.Union[t.Type[ExceptionWithCode], t.Sequence[t.Type[ExceptionWithCode]]]
