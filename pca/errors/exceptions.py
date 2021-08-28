import json
import typing as t

from copy import deepcopy


if t.TYPE_CHECKING:
    from .catalog import ErrorCatalog


class ExceptionWithCode(Exception):
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

    code: str = ""
    area: str = ""
    hint: str = ""
    params: t.Dict[str, t.Any] = None
    catalog: "ErrorCatalog" = None

    def __init__(self, code: str = None, area: str = None, hint: str = None, params: dict = None):
        if code:
            self.__dict__["code"] = code
        if area:
            self.__dict__["area"] = area
        if hint:
            self.__dict__["hint"] = hint
        self.__dict__["params"] = params if params else {}

    def __set_name__(self, owner: t.Any, name: str) -> None:
        """
        Setting an instance on an ErrorCatalog subclass as a filed closely bounds both
        and can set default values to area/code fields.
        """
        from .catalog import ErrorCatalog

        if not issubclass(owner, ErrorCatalog):
            return
        self.__dict__["catalog"] = owner
        self.__dict__["code"] = self.code or name
        self.__dict__["area"] = self.area or self.catalog.default_area

    def __eq__(self, other: t.Any) -> bool:
        """
        Equality with accuracy to class type, `area` & `code` values.
        `params` are not relevant.
        """
        return (
            other.__class__ is self.__class__
            and self.code == other.code
            and self.area == other.area
        )

    def __hash__(self) -> int:
        """
        Hash compatible to __eq__. Doesn't take into account params.
        TODO notify when lack of params here is going to be a problem. __eq__ doesn't consider
        `params` on purpose, but this also means that any two instances of the same error class
        with the same `area/code` are equated.
        """
        return hash((self.__class__, self.code, self.area))

    def __setattr__(self, key, value) -> None:
        raise AttributeError(  # pragma: no cover
            "The instances of this class should be considered immutable."
        )

    @property
    def short_description(self) -> str:
        """
        Returns description that can be used to map errors to response value for a Presenter.
        """
        param_json = "/" + json.dumps(self.params) if self.params else ""
        return f"{self.area}/{self.code}{param_json}"

    def __repr__(self) -> str:
        params_str = f", params={self.params}" if self.params else ""
        return f"{self.__class__.__name__}(code='{self.code}', area='{self.area}'{params_str})"

    __str__ = __repr__

    def with_params(self, **kwargs) -> "ExceptionWithCode":
        """
        Clones the instance of error and sets kwargs as the new instance's params. Sets the
        same catalog.

        Used to supply logic-dependent params to the catalog-defined instance of an error.
        """
        copy: ExceptionWithCode = self.__class__(code=self.code, area=self.area, params=kwargs)
        copy.__dict__["catalog"] = self.catalog
        return copy

    def clone(self) -> "ExceptionWithCode":
        """
        Creates new identical copy of the error class, but doesn't consider the catalog iff
        defined.

        Used to set an error instance from one catalog to another one.
        """
        return self.__class__(code=self.code, area=self.area, params=deepcopy(self.params))
