from pca.errors import (
    ErrorCatalog,
    ExceptionWithCode,
)


class ExampleCatalog(ErrorCatalog):
    default_area = "EXAMPLE"

    FOO = ExceptionWithCode()
    BAR = ExceptionWithCode("CODE", "AREA")


class TestErrorCatalog:
    def test_explicit_arguments(self):
        assert ExampleCatalog.FOO.code == "FOO"  # based on field name
        assert ExampleCatalog.FOO.area == "EXAMPLE"  # based on catalog field

    def test_defaults(self):
        assert ExampleCatalog.BAR.code == "CODE"
        assert ExampleCatalog.BAR.area == "AREA"

    def test_catalog_ref(self):
        assert ExampleCatalog.FOO.catalog == ExampleCatalog

    def test_in(self):
        assert ExampleCatalog.FOO in ExampleCatalog

    def test_iter(self):
        # noinspection PyTypeChecker
        assert list(ExampleCatalog) == [ExampleCatalog.FOO, ExampleCatalog.BAR]

    def test_all(self):
        assert ExampleCatalog.all() == (ExampleCatalog.FOO, ExampleCatalog.BAR)

    def test_add_instance(self):
        instance = ExceptionWithCode("BAZ")
        ExampleCatalog.add_instance(instance)
        assert instance in ExampleCatalog
        # noinspection PyUnresolvedReferences
        assert ExampleCatalog.BAZ is instance

    def test_same_error_in_multiple_catalogs(self):
        class AnotherCatalog(ErrorCatalog):
            MY = ExampleCatalog.FOO.clone()

        assert AnotherCatalog.MY.catalog == AnotherCatalog
