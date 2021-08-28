import pytest

from pca.errors import (
    ErrorCatalog,
    ExceptionWithCode,
)


class TestCustomError:
    @pytest.fixture
    def instance(self):
        return ExceptionWithCode(code="code", area="area")

    @pytest.fixture
    def instance_with_params(self):
        return ExceptionWithCode(
            code="code",
            area="area",
            params={"foo": "bar"},
            hint="Some hint for fellow developers.",
        )

    @pytest.fixture
    def catalog(self):
        return object()

    def test_explicit_arguments(self, instance_with_params: ExceptionWithCode):
        assert instance_with_params.code == "code"
        assert instance_with_params.area == "area"
        assert instance_with_params.params == {"foo": "bar"}
        assert instance_with_params.catalog is None
        assert instance_with_params.hint == "Some hint for fellow developers."

    def test_defaults(self):
        instance = ExceptionWithCode()
        assert instance.code == ""
        assert instance.area == ""
        assert instance.params == {}
        assert instance.catalog is None

    def test_hint(self):
        instance = ExceptionWithCode(hint="Some hint for fellow developers.")
        assert instance.hint == "Some hint for fellow developers."
        assert instance.area == ""
        assert instance.params == {}
        assert instance.catalog is None

    def test_setting_catalog(self, instance: ExceptionWithCode):
        class MyCatalog(ErrorCatalog):
            a = instance

        assert instance.catalog is MyCatalog

    # noinspection PyUnusedLocal
    def test_not_setting_catalog(self, instance: ExceptionWithCode):
        class NotACatalog:
            a = instance

        assert instance.catalog is None

    def test_clone(self, instance_with_params: ExceptionWithCode, catalog):
        instance_with_params.__dict__["catalog"] = catalog
        cloned = instance_with_params.clone()
        assert cloned.code == "code"
        assert cloned.area == "area"
        assert cloned.params == {"foo": "bar"}
        assert cloned.catalog is None
        assert cloned == instance_with_params
        assert cloned is not instance_with_params
        assert cloned.params is not instance_with_params.params

    def test_with_params(self, instance: ExceptionWithCode, catalog):
        instance.__dict__["catalog"] = catalog
        cloned = instance.with_params(a=1)
        assert cloned.code == "code"
        assert cloned.area == "area"
        assert cloned.params == {"a": 1}
        assert cloned.catalog is catalog
        assert cloned == instance
        assert cloned is not instance

    def test_equality(self, instance: ExceptionWithCode, catalog):
        cloned = instance.clone()
        instance.__dict__["catalog"] = catalog
        assert instance == cloned
        assert instance != {}
        other_instance = ExceptionWithCode(
            code="code", area="area", params={"different": "params"}
        )
        assert instance == other_instance
        assert hash(instance) == hash(other_instance)

    def test_equality_while_different_params(
        self, instance: ExceptionWithCode, instance_with_params: ExceptionWithCode
    ):
        assert instance == instance_with_params
        assert instance.params != instance_with_params.params

    def test_repr(self, instance: ExceptionWithCode, instance_with_params: ExceptionWithCode):
        assert repr(instance) == "ExceptionWithCode(code='code', area='area')"
        assert repr(instance_with_params) == (
            "ExceptionWithCode(code='code', area='area', params={'foo': 'bar'})"
        )

    def test_short_description(
        self, instance: ExceptionWithCode, instance_with_params: ExceptionWithCode
    ):
        assert instance.short_description == "area/code"
        assert instance_with_params.short_description == 'area/code/{"foo": "bar"}'
