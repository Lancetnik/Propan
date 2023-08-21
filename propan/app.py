import logging
from abc import ABC
from typing import Any, Callable, Dict, List, Optional, Sequence, TypeVar, Union

import anyio
from pydantic import AnyHttpUrl

from propan._compat import ParamSpec
from propan.asyncapi.schema import (
    Contact,
    ContactDict,
    ExternalDocs,
    ExternalDocsDict,
    License,
    LicenseDict,
    Tag,
    TagDict,
)
from propan.broker.core.asyncronous import BrokerAsyncUsecase
from propan.cli.supervisors.utils import set_exit
from propan.log import logger
from propan.types import AnyCallable, AnyDict, AsyncFunc, SettingField
from propan.utils import apply_types, context
from propan.utils.functions import to_async

P_HookParams = ParamSpec("P_HookParams")
T_HookReturn = TypeVar("T_HookReturn")


class ABCApp(ABC):
    _on_startup_calling: List[AnyCallable]
    _after_startup_calling: List[AnyCallable]
    _on_shutdown_calling: List[AnyCallable]
    _after_shutdown_calling: List[AnyCallable]

    def __init__(
        self,
        broker: Optional[BrokerAsyncUsecase[Any, Any]] = None,
        logger: Optional[logging.Logger] = logger,
        # AsyncAPI information
        title: str = "Propan",
        version: str = "0.1.0",
        description: str = "",
        terms_of_service: Optional[AnyHttpUrl] = None,
        license: Optional[Union[License, LicenseDict, AnyDict]] = None,
        contact: Optional[Union[Contact, ContactDict, AnyDict]] = None,
        identifier: Optional[str] = None,
        tags: Optional[Sequence[Union[Tag, TagDict, AnyDict]]] = None,
        external_docs: Optional[Union[ExternalDocs, ExternalDocsDict, AnyDict]] = None,
    ):
        self.broker = broker
        self.logger = logger
        self.context = context
        context.set_global("app", self)

        self._on_startup_calling = []
        self._after_startup_calling = []
        self._on_shutdown_calling = []
        self._after_shutdown_calling = []

        # AsyncAPI information
        self.title = title
        self.version = version
        self.description = description
        self.terms_of_service = terms_of_service
        self.license = license
        self.contact = contact
        self.identifier = identifier
        self.asyncapi_tags = tags
        self.external_docs = external_docs

    def set_broker(self, broker: BrokerAsyncUsecase[Any, Any]) -> None:
        """Set already existed App object broker
        Usefull then you create/init broker in `on_startup` hook"""
        self.broker = broker

    def on_startup(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running BEFORE broker connected
        This hook also takes an extra CLI options as a kwargs"""
        self._on_startup_calling.append(apply_types(func))
        return func

    def on_shutdown(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running BEFORE broker disconnected"""
        self._on_shutdown_calling.append(apply_types(func))
        return func

    def after_startup(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running AFTER broker connected"""
        self._after_startup_calling.append(apply_types(func))
        return func

    def after_shutdown(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running AFTER broker disconnected"""
        self._after_shutdown_calling.append(apply_types(func))
        return func

    def _log(self, level: int, message: str) -> None:
        if self.logger is not None:
            self.logger.log(level, message)


class PropanApp(ABCApp):
    _on_startup_calling: List[AsyncFunc]
    _after_startup_calling: List[AsyncFunc]
    _on_shutdown_calling: List[AsyncFunc]
    _after_shutdown_calling: List[AsyncFunc]

    _stop_event: Optional[anyio.Event]

    def __init__(
        self,
        broker: Optional[BrokerAsyncUsecase[Any, Any]] = None,
        logger: Optional[logging.Logger] = logger,
        # AsyncAPI args,
        title: str = "Propan",
        version: str = "0.1.0",
        description: str = "",
        terms_of_service: Optional[AnyHttpUrl] = None,
        license: Optional[Union[License, LicenseDict, AnyDict]] = None,
        contact: Optional[Union[Contact, ContactDict, AnyDict]] = None,
        identifier: Optional[str] = None,
        tags: Optional[Sequence[Union[Tag, TagDict, AnyDict]]] = None,
        external_docs: Optional[Union[ExternalDocs, ExternalDocsDict, AnyDict]] = None,
    ):
        """Asyncronous Propan Application class

        stores and run broker, control hooks

        Args:
            broker: async broker to run (may be `None`, then specify by `set_broker`)
            logger: logger object to log startup/shutdown messages (`None` to disable)

        AsyncAPI Args:
            title: application title
            version: application version
            description: application description
        """
        super().__init__(
            broker=broker,
            logger=logger,
            title=title,
            version=version,
            description=description,
            terms_of_service=terms_of_service,
            license=license,
            contact=contact,
            identifier=identifier,
            tags=tags,
            external_docs=external_docs,
        )

        self._stop_event = None

        set_exit(lambda *_: self.__exit())

    def on_startup(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running BEFORE broker connected

        This hook also takes an extra CLI options as a kwargs

        Args:
            func: async or sync func to call as a hook

        Returns:
            Async version of the func argument
        """
        super().on_startup(to_async(func))
        return func

    def on_shutdown(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running BEFORE broker disconnected

        Args:
            func: async or sync func to call as a hook

        Returns:
            Async version of the func argument
        """
        super().on_shutdown(to_async(func))
        return func

    def after_startup(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running AFTER broker connected

        Args:
            func: async or sync func to call as a hook

        Returns:
            Async version of the func argument
        """
        super().after_startup(to_async(func))
        return func

    def after_shutdown(
        self,
        func: Callable[P_HookParams, T_HookReturn],
    ) -> Callable[P_HookParams, T_HookReturn]:
        """Add hook running AFTER broker disconnected

        Args:
            func: async or sync func to call as a hook

        Returns:
            Async version of the func argument
        """
        super().after_shutdown(to_async(func))
        return func

    async def run(
        self,
        log_level: int = logging.INFO,
        run_extra_options: Optional[Dict[str, SettingField]] = None,
    ) -> None:
        """Run Propan Application

        Args:
            log_level: force application log level

        Returns:
            Block an event loop until stopped
        """
        assert self.broker, "You should setup a broker"

        self._init_async_cycle()
        async with anyio.create_task_group() as tg:
            tg.start_soon(self._start, log_level, run_extra_options)
            await self._stop(log_level)
            tg.cancel_scope.cancel()

    def _init_async_cycle(self) -> None:
        if self._stop_event is None:
            self._stop_event = anyio.Event()

    async def _start(
        self,
        log_level: int = logging.INFO,
        run_extra_options: Optional[Dict[str, SettingField]] = None,
    ) -> None:
        self._log(log_level, "Propan app starting...")
        await self._startup(**(run_extra_options or {}))
        self._log(log_level, "Propan app started successfully! To exit press CTRL+C")

    async def _stop(self, log_level: int = logging.INFO) -> None:
        assert self._stop_event, "You should call `_init_async_cycle` first"
        await self._stop_event.wait()
        self._stop_event = None

        self._log(log_level, "Propan app shutting down...")
        await self._shutdown()
        self._log(log_level, "Propan app shut down gracefully.")

    async def _startup(self, **run_extra_options: SettingField) -> None:
        for func in self._on_startup_calling:
            await func(**run_extra_options)

        if self.broker is not None:
            await self.broker.start()

        for func in self._after_startup_calling:
            await func()

    async def _shutdown(self) -> None:
        for func in self._on_shutdown_calling:
            await func()

        if self.broker is not None:
            await self.broker.close()

        for func in self._after_shutdown_calling:
            await func()

    def __exit(self) -> None:
        if self._stop_event is not None:  # pragma: no branch
            self._stop_event.set()
