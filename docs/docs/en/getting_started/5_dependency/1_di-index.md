---
nested: A nested dependency is called here
---

# Dependencies

**Propan** uses the secondary library [**FastDepends**](https://lancetnik.github.io/FastDepends/){target="_blank"} for dependency management.
This dependency system is literally borrowed from **FastAPI**, so if you know how to work with this framework, you know how to work with dependencies in Propan.

You can go to the documentation [**FastDepends**](https://lancetnik.github.io/FastDepends/){target="_blank"} if you want to get more details, however, the key points and **additions** will be covered here.

## Type casting

The key function in the dependency management and type conversion system in *Propan* is the decorator `@apply_types` (@inject in FastDepends).

By default, it applies to all event handlers, unless you disabled the same option at a broker creation.

{! includes/getting_started/dependencies/depends/1.md !}

!!! warning
    By setting the `apply_types=False` flag, you disable not only type casting, but also `Depends` and `Context`.

This flag can be useful if you are using **Propan** within another framework and you do not need to use
a native dependency system.

## Dependency Injection

To implement dependencies in **Propan**, a special class **Depends** is used

{! includes/getting_started/dependencies/depends/2.md !}

**The first step**: we need to declare a dependency - it can be any `Callable` object.

??? note "Callable"
    "Callable" is an object that can be "called". It can be a function, a class, or a class method.

    In other words: if you can write such code `my_object()` - `my_object` will be `Callable`

{! includes/getting_started/dependencies/depends/3.md !}

**Second step**: Declare which dependencies you need using `Depends`

{! includes/getting_started/dependencies/depends/4.md !}

**The last step**: Just use the result of executing your dependency!

It's easy, isn't it?

!!! tip "Auto @apply_types"
    In the code above, we didn't use this decorator for our dependencies. However, it still applies
    to all functions used as dependencies. Keep this in your mind.

## Nested dependencies

Dependencies can also contain other dependencies. This works in a very predictable way: just declare
`Depends` in the dependent function.

{% import 'getting_started/dependencies/depends/5.md' as includes with context %}
{{ includes }}


!!! Tip "Caching"
    In the example above, the `another_dependency` function will be called at **ONCE!**.
    `Propan` caches all dependency execution results within **ONE** `@apply_stack` call stack.
    This means that all nested dependencies will receive the cached result of dependency execution.
    But, between different calls of the main function, these results will be different.

    To prevent this behavior, just use `Depends(..., cache=False)`. In this case, the dependency will be used for each function
    in the call stack where it is used.

## Use with regular functions

You can use the decorator `@apply_types` not only together with your `@broker.hanle', but also with the usual functions: both synchronous and asynchronous.

=== "Sync"
    ```python hl_lines="3-4" linenums="1"
    {!> docs_src/quickstart/dependencies/basic/3_sync.py !}
    ```

=== "Async"
    ```python hl_lines="4-5 7-8" linenums="1"
    {!> docs_src/quickstart/dependencies/basic/3_async.py !}
    ```

    !!! tip "Be careful"
        In asynchronous code, you can use both synchronous and asynchronous dependencies.
        But in synchronous code, only synchronous dependencies are available to you.

## Casting dependency types

**FastDepends**, used by **Propan**, also gives the type `return`. This means that the value returned by the dependency will be
be cast to the type twice: as `return` these are dependencies and as the input argument of the main function. This does not incur additional costs if
these types have the same annotation. Just keep it in mind. Or not... Anyway, I've warned you.

```python linenums="1"
from propan import Depends, apply_types

def simple_dependency(a: int, b: int = 3) -> str:
    return a + b  # 'return' is cast to `str` for the first time

@inject
def method(a: int, d: int = Depends(simple_dependency)):
    # 'd' is cast to `int` for the second time
    return a + d

assert method("1") == 5
```

Also, the result of executing the dependency is cached. If you use this dependency in `N` functions,
this cached result will be converted to type `N` times (at the input to the function being used).

To avoid problems with this, use [mypy](https://www.mypy-lang.org){target="_blank"} or just be careful with the annotation
of types in your project.
