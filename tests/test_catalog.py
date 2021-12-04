import typing as t

from pca.packages.errors import (
    ErrorCatalog,
    ExceptionWithCode,
    error_builder,
)


class ExampleCatalog(ErrorCatalog):
    Foo: t.Type[ExceptionWithCode] = error_builder()
    Bar: t.Type[ExceptionWithCode] = error_builder("MyBar")


class TestErrorCatalog:
    def test_explicit_arguments(self):
        assert ExampleCatalog.Foo.code == "Foo"  # based on field name

    def test_defaults(self):
        assert ExampleCatalog.Bar.code == "MyBar"  # explicitely named

    def test_catalog_ref(self):
        assert ExampleCatalog.Foo.catalog == ExampleCatalog

    def test_in(self):
        assert ExampleCatalog.Foo in ExampleCatalog

    def test_iter(self):
        assert list(ExampleCatalog) == [ExampleCatalog.Foo, ExampleCatalog.Bar]

    def test_all(self):
        assert ExampleCatalog.all() == (ExampleCatalog.Foo, ExampleCatalog.Bar)

    def test_add_instance(self):
        instance = error_builder("Baz")
        ExampleCatalog.add_instance(instance)
        assert instance in ExampleCatalog
        assert ExampleCatalog.Baz is instance  # type: ignore
