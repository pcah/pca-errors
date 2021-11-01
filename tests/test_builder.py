import pytest

from pca.errors import (
    ErrorCatalog,
    ExceptionWithCode,
    error_builder,
)


@pytest.fixture
def error_class():
    return error_builder("MyError")


@pytest.fixture
def error_instance(error_class):
    return error_class()


@pytest.fixture
def error_instance_with_kwargs(error_class):
    return error_class("an_arg", foo="bar")


@pytest.fixture
def catalog():
    return ErrorCatalog()


class TestErrorBuilder:
    def test_repr_on_class(self):
        assert repr(error_builder("MyError", hint="hint")) == "<MyError>"

    def test_repr_on_instance(self, error_class):
        assert repr(error_class()) == "MyError()"
        assert repr(error_class("arg1", "arg2")) == "MyError('arg1', 'arg2')"
        assert repr(error_class(foo="bar", baz="quax")) == "MyError(foo='bar', baz='quax')"
        assert (
            repr(error_class("arg1", "arg2", foo="bar", baz="quax"))
            == "MyError('arg1', 'arg2', foo='bar', baz='quax')"
        )

    def test_explicit_arguments(self, error_class, error_instance_with_kwargs: ExceptionWithCode):
        assert error_instance_with_kwargs.code == "MyError"
        assert error_instance_with_kwargs.cls == error_class
        assert error_instance_with_kwargs.args == ("an_arg",)
        assert error_instance_with_kwargs.kwargs == {"foo": "bar"}
        assert error_instance_with_kwargs.catalog is None
        assert error_instance_with_kwargs.hint == ""

    def test_error_kwargs(self, error_instance_with_kwargs: ExceptionWithCode):
        error_instance_with_kwargs.foo = "bar"

        with pytest.raises(AttributeError):
            error_instance_with_kwargs.bar

    def test_defaults(self, error_class):
        instance = error_class()
        assert instance.code == "MyError"
        assert instance.kwargs == {}
        assert instance.catalog is None

    def test_class_with_hint(self):
        hint = "Some hint for fellow developers."
        error_class = error_builder(
            "MyError",
            hint=hint,
        )
        instance = error_class()
        assert instance.hint == hint
        assert instance.kwargs == {}

    def test_conforms(self, error_class, error_instance):
        assert error_class.conforms(error_instance)
        assert error_instance.is_conforming(error_class)
        assert not error_instance.is_conforming(ValueError)

    def test_conforms_base_class(self):
        error_class = error_builder("SomeError", bases=ValueError)
        error_instance = error_class(foo="bar")
        assert error_class.conforms(error_instance)
        assert error_instance.is_conforming(error_class)
        assert error_instance.is_conforming(ValueError)

    def test_clone(self, error_class, error_instance_with_kwargs):
        cloned = error_instance_with_kwargs.clone(foo="spam", bar="eggs")
        assert cloned.cls == error_class
        assert cloned.to_dict() == {
            "code": "MyError",
            "catalog": None,
            "kwargs": {"bar": "eggs", "foo": "spam"},
        }


class TestErrorCatching:
    def test_single_inheritance(self):
        class MyBaseClass(Exception):
            pass

        error_class = error_builder("MyError", bases=MyBaseClass)
        with pytest.raises(error_class) as error_info:
            raise error_class
        assert error_info.value.cls == error_class

    def test_multi_inheritance(self):
        class MyBaseClass(Exception):
            pass

        error_class = error_builder("MyError", bases=(MyBaseClass, ValueError))
        with pytest.raises(ValueError) as error_info:
            raise error_class
        assert isinstance(error_info.value, error_class)
        assert isinstance(error_info.value, ValueError)

    def test_instance_with_kwargs_raised(self, error_class):
        with pytest.raises(error_class) as error_info:
            raise error_class("arg1", foo="bar")
        instance = error_info.value
        assert instance.cls == error_class
        assert instance.args == ("arg1",)
        assert instance.kwargs == {"foo": "bar"}


class TestIntegrationWithCatalog:
    def test_setting_catalog(self):
        class MyCatalog(ErrorCatalog):
            SomeName = error_builder("OtherName", hint="hint")

        assert MyCatalog.SomeName.catalog is MyCatalog
        assert repr(MyCatalog.SomeName) == "<OtherName catalog=MyCatalog>"

    # noinspection PyUnusedLocal
    def test_not_setting_catalog(self, error_class: ExceptionWithCode):
        class NotACatalog:
            SomeName = error_builder("OtherName", hint="hint")

        assert error_class.catalog is None
        assert repr(NotACatalog.SomeName) == "<OtherName>"

    def test_catalog_sets_name(self):
        class MyCatalog(ErrorCatalog):
            SomeName = error_builder(hint="hint")

        assert repr(MyCatalog.SomeName) == "<SomeName catalog=MyCatalog>"
        assert MyCatalog.SomeName.__name__ == "SomeName"
