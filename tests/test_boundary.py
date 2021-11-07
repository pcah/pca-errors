from collections import namedtuple

import mock
import pytest

from pca.errors import ErrorBoundary


Callbacks = namedtuple(
    "Callbacks",
    [
        "log_inner_error",
        "should_propagate_exception",
        "transform_propagated_exception",
        "on_no_exception",
        "on_propagate_exception",
        "on_suppress_exception",
    ],
)


class AnException(Exception):
    pass


class AnotherException(Exception):
    pass


@pytest.fixture
def catchall_boundary():
    return ErrorBoundary()


@pytest.fixture
def specific_boundary():
    return ErrorBoundary(catch=AnException)


@pytest.fixture
def callbacks():
    return Callbacks(
        log_inner_error=mock.Mock(),
        should_propagate_exception=mock.Mock(return_value=False),
        transform_propagated_exception=mock.Mock(return_value=None),
        on_no_exception=mock.Mock(),
        on_propagate_exception=mock.Mock(),
        on_suppress_exception=mock.Mock(),
    )


@pytest.fixture
def boundary_with_callbacks(callbacks):
    return ErrorBoundary(**callbacks._asdict())


class TestNotRaised:
    def test_catchall_as_context_manager(self, catchall_boundary):
        with catchall_boundary as error_boundary:
            pass
        assert error_boundary.exc_info is error_boundary.exc_info

    def test_callbacks(self, boundary_with_callbacks, callbacks):
        with boundary_with_callbacks:
            pass
        callbacks.log_inner_error.assert_not_called()
        callbacks.should_propagate_exception.assert_not_called()
        callbacks.transform_propagated_exception.assert_not_called()
        callbacks.on_no_exception.assert_called_once_with()
        callbacks.on_propagate_exception.assert_not_called()
        callbacks.on_suppress_exception.assert_not_called()


class TestCatching:
    def test_catchall_as_context_manager(self, catchall_boundary):
        exception = AnException()
        with catchall_boundary as error_boundary:
            raise exception
        assert error_boundary.exc_info.value is exception

    def test_catchall_as_decorator(self, catchall_boundary):
        exception = AnException()

        @catchall_boundary
        def foo():
            raise exception

        foo()
        assert catchall_boundary.exc_info.value is exception

    def test_specific_catching(self, specific_boundary):
        exception = AnException()
        with specific_boundary as error_boundary:
            raise exception
        assert error_boundary.exc_info.value is exception

    def test_callbacks(self, boundary_with_callbacks, callbacks):
        exception = AnException()
        with boundary_with_callbacks:
            raise exception
        callbacks.log_inner_error.assert_not_called()
        callbacks.should_propagate_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.transform_propagated_exception.assert_not_called()
        callbacks.on_no_exception.assert_not_called()
        callbacks.on_propagate_exception.assert_not_called()
        callbacks.on_suppress_exception.assert_called_once_with(boundary_with_callbacks.exc_info)


class TestPropagating:
    def test_specific_catching(self, specific_boundary):
        exception = AnotherException()
        with pytest.raises(AnotherException) as error_info:
            with specific_boundary:
                raise exception
        assert error_info.value is exception

    def test_callbacks(self, boundary_with_callbacks, callbacks):
        exception = AnException()
        callbacks.should_propagate_exception.return_value = True
        with pytest.raises(AnException):
            with boundary_with_callbacks:
                raise exception
        callbacks.log_inner_error.assert_not_called()
        callbacks.should_propagate_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.transform_propagated_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.on_no_exception.assert_not_called()
        callbacks.on_propagate_exception.assert_called_once_with(boundary_with_callbacks.exc_info)
        callbacks.on_suppress_exception.assert_not_called()

    def test_transform_propagated_exception(self, boundary_with_callbacks, callbacks):
        exception = AnException()
        transformed_exception = AnotherException()
        callbacks.should_propagate_exception.return_value = True
        callbacks.transform_propagated_exception.return_value = transformed_exception

        with pytest.raises(AnotherException) as error_info:
            with boundary_with_callbacks:
                raise exception

        assert error_info.value is transformed_exception
        callbacks.log_inner_error.assert_not_called()
        callbacks.should_propagate_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.transform_propagated_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.on_no_exception.assert_not_called()
        callbacks.on_propagate_exception.assert_called_once_with(boundary_with_callbacks.exc_info)
        callbacks.on_suppress_exception.assert_not_called()
