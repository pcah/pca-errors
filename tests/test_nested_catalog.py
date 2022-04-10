import typing as t

from pca.packages.errors import (
    ErrorCatalog,
    ExceptionWithCode,
    error_builder,
)


class ExternalCatalog(ErrorCatalog):
    ExternalError: t.Type[ExceptionWithCode] = error_builder()


class CompositeCatalog(ErrorCatalog):
    OwnError: t.Type[ExceptionWithCode] = error_builder()
    ExternalCatalog = ExternalCatalog

    class NestedCatalog(ErrorCatalog):
        NestedError: t.Type[ExceptionWithCode] = error_builder()


def test_subcatalogs() -> None:
    assert ExternalCatalog.subcatalogs() == ()
    assert CompositeCatalog.subcatalogs() == (ExternalCatalog, CompositeCatalog.NestedCatalog)


def test_repr() -> None:
    assert repr(CompositeCatalog.NestedCatalog) == (
        "test_nested_catalog.CompositeCatalog.NestedCatalog"
    )
    assert repr(CompositeCatalog.ExternalCatalog) == "test_nested_catalog.ExternalCatalog"


def test_all() -> None:
    assert CompositeCatalog.all() == (
        CompositeCatalog.OwnError,
        ExternalCatalog.ExternalError,
        CompositeCatalog.NestedCatalog.NestedError,
    )


def test_len() -> None:
    assert len(CompositeCatalog.NestedCatalog) == 1
    assert len(CompositeCatalog) == 3


def test_contains() -> None:
    assert CompositeCatalog.NestedCatalog.NestedError in CompositeCatalog
    assert ExternalCatalog.ExternalError in CompositeCatalog
