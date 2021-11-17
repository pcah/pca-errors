import logging
import typing as t

from functools import wraps

from .types import (
    ExceptionInfo,
    ExceptionTypeOrTypes,
)


__all__ = ("ErrorBoundary",)


class ErrorBoundary:

    exc_info: t.Optional[ExceptionInfo] = None

    def __init__(
        self,
        name: t.Optional[str] = None,
        catch: ExceptionTypeOrTypes = Exception,
        log_inner_error: t.Callable[["ErrorBoundary", str, Exception], None] = None,
        should_propagate_exception: t.Callable[["ErrorBoundary", ExceptionInfo], bool] = None,
        transform_propagated_exception: t.Callable[
            ["ErrorBoundary", ExceptionInfo], t.Optional[Exception]
        ] = None,
        on_no_exception: t.Callable[["ErrorBoundary"], None] = None,
        on_propagate_exception: t.Callable[["ErrorBoundary", ExceptionInfo], None] = None,
        on_suppress_exception: t.Callable[["ErrorBoundary", ExceptionInfo], None] = None,
    ) -> None:
        """
        :param name:
        :param catch:
        :param log_inner_error:
        :param should_propagate_exception:
        :param transform_propagated_exception:
        :param on_no_exception:
        :param on_propagate_exception:
        :param on_suppress_exception:
        """
        self.name = str(id(self)) if name is None else name
        # TODO py-compatibility: __future__.annotations & removing " from typing of the class
        self.catch = catch
        # for all the callbacks, if defined, override appropriate methods instance-wide without
        # inheritance
        if log_inner_error:
            self.log_inner_error = log_inner_error  # type: ignore
        if should_propagate_exception:
            self.should_propagate_exception = should_propagate_exception  # type: ignore
        if transform_propagated_exception:
            self.transform_propagated_exception = transform_propagated_exception  # type: ignore
        if on_no_exception:
            self.on_no_exception = on_no_exception  # type: ignore
        if on_propagate_exception:
            self.on_propagate_exception = on_propagate_exception  # type: ignore
        if on_suppress_exception:
            self.on_suppress_exception = on_suppress_exception  # type: ignore

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name={repr(self.name)})"

    def __call__(self, func: t.Callable) -> t.Callable:
        @wraps(func)
        def inner(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return inner

    def __enter__(self):
        """Return `self` upon entering the runtime context."""
        return self

    def __exit__(self, *exc_info) -> bool:
        """Raise any exception triggered within the runtime context."""
        exc_info = self.exc_info = ExceptionInfo(*exc_info)
        if exc_info.type is None:
            try:
                self.on_no_exception()
            except Exception as e:
                self.log_inner_error("on_no_exception", exc_info.value, e)
            return False

        try:
            should_propagate = self.should_propagate_exception(exc_info)
        except Exception as e:
            should_propagate = True
            self.log_inner_error("should_propagate_exception", exc_info.value, e)
        if bool(should_propagate):
            try:
                self.on_propagate_exception(exc_info)
            except Exception as e:
                self.log_inner_error("on_propagate_exception", exc_info.value, e)
            try:
                transformed_exception = self.transform_propagated_exception(exc_info)
            except Exception as e:
                transformed_exception = None
                self.log_inner_error("transform_propagated_exception", exc_info.value, e)
                # reraise original exception, because now the traceback module remembers
                # the last occurence (the error from callback), not the original error
                raise exc_info.value
            if transformed_exception:
                raise transformed_exception from exc_info.value
            return False

        try:
            self.on_suppress_exception(exc_info)
        except Exception as e:
            self.log_inner_error("on_suppress_exception", exc_info.value, e)
        return True

    def log_inner_error(
        self, where: str, main_error: t.Optional[BaseException], callback_error: Exception
    ) -> None:
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.

        Called when an exception is raised by the mechanics of `ErrorBoundary` itself.
        The boundary tries hard not to break code control as it is intended to guarantee the code
        control flow to be smooth around the boundary. The `log_inner_error` callable should be
        a window to notify about problems around its usage.

        By default, it logs the error using stdlib `logging` mechanics.
        """
        inner_logger = logging.getLogger(__name__)
        handled_text = f" while {repr(main_error)} was handled" if main_error is not None else ""
        # breakpoint()
        inner_logger.exception(
            f"{str(self)}.{where} callback raised unhandled error: {repr(callback_error)} was "
            f"raised{handled_text}."
        )

    def on_no_exception(self):
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.
        Called on exiting boundary and no exception has happened.

        It does nothing by default.
        """

    def should_propagate_exception(self, exc_info: ExceptionInfo) -> bool:
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.
        States whether the exception catched by the boundary should be propagated (aka reraised)
        or silenced.

        Silences all catched errors by default.
        """
        return not self.catch or not isinstance(exc_info.value, self.catch)

    def transform_propagated_exception(self, exc_info: ExceptionInfo) -> t.Optional[Exception]:
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.
        Called on to check whether catched exception should be transformed into another instance
        and raised.

        NB: (re)raising original exception instance is done automatically by the mechanics of
        context managers: https://docs.python.org/3/reference/datamodel.html#object.__exit__
        To have another exception raised, you have to raise it by yourself inside this function.

        It does not transform the exception by default.
        """
        return None

    def on_propagate_exception(self, exc_info: ExceptionInfo) -> None:
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.
        Called on exiting boundary when exception will be raised.

        It does nothing by default.
        """

    def on_suppress_exception(self, exc_info: ExceptionInfo) -> None:
        """
        Hook method, that can be overriden using `ErrorBoundary` constructor.
        Called on exiting boundary when exception will be silenced.

        By default it logs the error using default logger on WARNING level.
        """
        inner_logger = logging.getLogger(__name__)
        inner_logger.warning(repr(exc_info.value), exc_info=True)
