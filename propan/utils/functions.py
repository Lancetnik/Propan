import inspect
from functools import wraps
from typing import Awaitable, Callable, List, Union, cast

from fast_depends.utils import run_async as call_or_await

from propan.types import AnyCallable, F_Return, F_Spec

__all__ = (
    "call_or_await",
    "get_function_positional_arguments",
    "to_async",
)


def to_async(
    func: Union[
        Callable[F_Spec, F_Return],
        Callable[F_Spec, Awaitable[F_Return]],
    ]
) -> Callable[F_Spec, Awaitable[F_Return]]:
    @wraps(func)
    async def to_async_wrapper(*args: F_Spec.args, **kwargs: F_Spec.kwargs) -> F_Return:
        r = await call_or_await(func, *args, **kwargs)
        return cast(F_Return, r)

    return to_async_wrapper


def get_function_positional_arguments(func: AnyCallable) -> List[str]:
    signature = inspect.signature(func)

    arg_kinds = (
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    )

    return [
        param.name for param in signature.parameters.values() if param.kind in arg_kinds
    ]


def patch_annotation(
    func: Callable[F_Spec, F_Return]
) -> Callable[[Callable[..., F_Return]], Callable[F_Spec, F_Return],]:
    def patch_annotation_wrapper(
        wrapper: Callable[..., F_Return]
    ) -> Callable[F_Spec, F_Return]:
        return wraps(func)(wrapper)

    return patch_annotation_wrapper
