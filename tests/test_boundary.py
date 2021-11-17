import sys

from collections import namedtuple

import mock
import pytest

from pca.errors import ErrorBoundary


PY36 = (3, 6) <= sys.version_info < (3, 7)

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
    return ErrorBoundary(name="boundary_with_callbacks", **callbacks._asdict())


class TestNotRaised:
    def test_catchall_as_context_manager(self, catchall_boundary) -> None:
        with catchall_boundary as error_boundary:
            pass
        assert error_boundary.exc_info is error_boundary.exc_info

    def test_callbacks(self, boundary_with_callbacks, callbacks) -> None:
        with boundary_with_callbacks:
            pass
        callbacks.should_propagate_exception.assert_not_called()
        callbacks.transform_propagated_exception.assert_not_called()
        callbacks.on_no_exception.assert_called_once_with()
        callbacks.on_propagate_exception.assert_not_called()
        callbacks.on_suppress_exception.assert_not_called()


class TestCatching:
    def test_catchall_as_context_manager(self, catchall_boundary) -> None:
        exception = AnException()
        with catchall_boundary as error_boundary:
            raise exception
        assert error_boundary.exc_info.value is exception  # type: ignore

    def test_catchall_as_decorator(self, catchall_boundary) -> None:
        exception = AnException()

        @catchall_boundary
        def foo() -> None:
            raise exception

        foo()
        assert catchall_boundary.exc_info.value is exception  # type: ignore

    def test_specific_catching(self, specific_boundary) -> None:
        exception = AnException()
        with specific_boundary as error_boundary:
            raise exception
        assert error_boundary.exc_info.value is exception

    def test_callbacks(self, boundary_with_callbacks, callbacks) -> None:
        exception = AnException()
        with boundary_with_callbacks:
            raise exception
        # type: ignore
        callbacks.should_propagate_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.transform_propagated_exception.assert_not_called()
        callbacks.on_no_exception.assert_not_called()
        callbacks.on_propagate_exception.assert_not_called()
        callbacks.on_suppress_exception.assert_called_once_with(boundary_with_callbacks.exc_info)


class TestPropagating:
    def test_specific_catching(self, specific_boundary) -> None:
        exception = AnotherException()
        with pytest.raises(AnotherException) as error_info:
            with specific_boundary:
                raise exception
        assert error_info.value is exception  # type: ignore

    def test_callbacks(self, boundary_with_callbacks, callbacks) -> None:
        exception = AnException()
        callbacks.should_propagate_exception.return_value = True
        with pytest.raises(AnException):
            with boundary_with_callbacks:
                raise exception
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
        callbacks.should_propagate_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.transform_propagated_exception.assert_called_once_with(
            boundary_with_callbacks.exc_info
        )
        callbacks.on_no_exception.assert_not_called()
        callbacks.on_propagate_exception.assert_called_once_with(boundary_with_callbacks.exc_info)
        callbacks.on_suppress_exception.assert_not_called()


class TestCallbackErrors:
    """
    Tests checking what happens when a callback throws an error.
    """

    @pytest.mark.skipif(
        PY36,
        reason="strange behavior of representing Exception.args on CPython 3.6.15; waiting for obsoletion for Py36",
    )
    def test_log_inner_error(self, caplog) -> None:
        main_exception = AnException("main_exception")
        callback_exception = AnotherException("callback_exception")
        boundary_with_callbacks = ErrorBoundary(name="boundary_with_callbacks")

        boundary_with_callbacks.log_inner_error(
            where="foo", main_error=main_exception, callback_error=callback_exception
        )

        assert caplog.messages == [
            (
                "ErrorBoundary(name='boundary_with_callbacks').foo callback raised unhandled "
                "error: AnotherException('callback_exception') was raised while "
                "AnException('main_exception') was handled."
            )
        ]

    def test_on_no_exception(self, boundary_with_callbacks, callbacks, caplog) -> None:
        callback_exception = AnotherException("callback_exception")
        callbacks.on_no_exception.side_effect = callback_exception

        with boundary_with_callbacks:
            pass

        callbacks.log_inner_error.assert_called_once_with(
            "on_no_exception", None, callback_exception
        )

    def test_should_propagate_exception(self, boundary_with_callbacks, callbacks, caplog) -> None:
        main_exception = AnException("main_exception")
        callback_exception = AnotherException("callback_exception")
        callbacks.should_propagate_exception.side_effect = callback_exception

        with pytest.raises(AnException) as error_info:
            with boundary_with_callbacks:
                raise main_exception

        assert error_info.value is main_exception
        callbacks.log_inner_error.assert_called_once_with(
            "should_propagate_exception", main_exception, callback_exception
        )

    def test_on_propagate_exception(self, boundary_with_callbacks, callbacks) -> None:
        main_exception = AnException("main_exception")
        callback_exception = AnotherException("callback_exception")
        callbacks.should_propagate_exception.return_value = True
        callbacks.on_propagate_exception.side_effect = callback_exception

        with pytest.raises(AnException) as error_info:
            with boundary_with_callbacks:
                raise main_exception

        assert error_info.value is main_exception
        callbacks.log_inner_error.assert_called_once_with(
            "on_propagate_exception", main_exception, callback_exception
        )

    def test_transform_propagated_exception(self, boundary_with_callbacks, callbacks) -> None:
        main_exception = AnException("main_exception")
        callback_exception = AnotherException("callback_exception")
        callbacks.should_propagate_exception.return_value = True
        callbacks.transform_propagated_exception.side_effect = callback_exception

        with pytest.raises(AnException) as error_info:
            with boundary_with_callbacks:
                raise main_exception

        assert error_info.value is main_exception
        callbacks.log_inner_error.assert_called_once_with(
            "transform_propagated_exception", main_exception, callback_exception
        )

    def test_on_suppress_exception(self, boundary_with_callbacks, callbacks) -> None:
        main_exception = AnException("main_exception")
        callback_exception = AnotherException("callback_exception")
        callbacks.on_suppress_exception.side_effect = callback_exception

        with boundary_with_callbacks:
            raise main_exception

        callbacks.log_inner_error.assert_called_once_with(
            "on_suppress_exception", main_exception, callback_exception
        )
