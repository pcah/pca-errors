"""
What would happen if someone want to do ErrorCatalog inheritance?

It's not a typical usecase for ErrorCatalog, but it might be necessity when you need to modify
an ErrorCatalog that you don't control, i.e. a catalog from 3rd party library.

If you want to see a typical catalog composition, take a look at `test_nested_catalog.py`
test module.
"""
from pca.packages.errors import (
    ErrorCatalog,
    error_builder,
)


class FooCatalog(ErrorCatalog):
    Foo = error_builder()


class BarCatalog(FooCatalog):
    Bar = error_builder()

    class NestedCatalog(ErrorCatalog):
        Nested = error_builder()

    class NestedOverriddenCatalog(ErrorCatalog):
        NestedOverridden = error_builder()


class BazCatalog(BarCatalog):
    Baz = error_builder()

    class NestedOverriddenCatalog(ErrorCatalog):
        NewNestedOverridden = error_builder()


def test_super_catalogs():
    assert tuple(FooCatalog._super_catalogs) == (FooCatalog,)
    assert tuple(BarCatalog._super_catalogs) == (FooCatalog, BarCatalog)
    assert tuple(BazCatalog._super_catalogs) == (
        FooCatalog,
        BarCatalog,
        BazCatalog,
    )


def test_nested_catalogs():
    assert FooCatalog._nested_catalogs == {}
    assert BarCatalog._nested_catalogs == {
        "NestedCatalog": BarCatalog.NestedCatalog,
        "NestedOverriddenCatalog": BarCatalog.NestedOverriddenCatalog,
    }
    assert BazCatalog._nested_catalogs == {
        "NestedCatalog": BazCatalog.NestedCatalog,
        "NestedOverriddenCatalog": BazCatalog.NestedOverriddenCatalog,
    }


def test_all():
    assert FooCatalog.all == (FooCatalog.Foo,)
    assert BarCatalog.all == (
        FooCatalog.Foo,
        BarCatalog.Bar,
        BarCatalog.NestedCatalog.Nested,
        BarCatalog.NestedOverriddenCatalog.NestedOverridden,
    )
    assert BazCatalog.all == (
        FooCatalog.Foo,
        BarCatalog.Bar,
        BazCatalog.Baz,
        BazCatalog.NestedCatalog.Nested,
        BazCatalog.NestedOverriddenCatalog.NewNestedOverridden,
    )
