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

        class DoublyNestedCatalog(ErrorCatalog):
            DoublyNested: t.Type[ExceptionWithCode] = error_builder()


def test_nested_catalogs() -> None:
    assert ExternalCatalog._nested_catalogs == {}
    assert CompositeCatalog._nested_catalogs == {
        "ExternalCatalog": ExternalCatalog,
        "NestedCatalog": CompositeCatalog.NestedCatalog,
    }


def test_repr() -> None:
    assert repr(CompositeCatalog.NestedCatalog) == (
        "test_nested_catalog.CompositeCatalog.NestedCatalog"
    )
    assert repr(CompositeCatalog.ExternalCatalog) == "test_nested_catalog.ExternalCatalog"


def test_all() -> None:
    assert CompositeCatalog.all == (
        CompositeCatalog.OwnError,
        ExternalCatalog.ExternalError,
        CompositeCatalog.NestedCatalog.NestedError,
        CompositeCatalog.NestedCatalog.DoublyNestedCatalog.DoublyNested,
    )


def test_len() -> None:
    assert len(CompositeCatalog.NestedCatalog) == 2
    assert len(CompositeCatalog) == 4


def test_contains() -> None:
    assert CompositeCatalog.NestedCatalog.NestedError in CompositeCatalog
    assert ExternalCatalog.ExternalError in CompositeCatalog
