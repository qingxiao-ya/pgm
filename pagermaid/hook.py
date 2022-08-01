import asyncio
import sys

from pyrogram import StopPropagation

from pagermaid import hook_functions, logs
from pagermaid.inject import inject
from pagermaid.single_utils import Message


class Hook:
    @staticmethod
    def on_startup():
        """
        注册一个启动钩子
        """
        def decorator(function):
            hook_functions["startup"].add(function)
            return function
        return decorator

    @staticmethod
    def on_shutdown():
        """
        注册一个关闭钩子
        """
        def decorator(function):
            hook_functions["shutdown"].add(function)
            return function
        return decorator

    @staticmethod
    def command_preprocessor():
        """
        注册一个命令预处理钩子
        """

        def decorator(function):
            hook_functions["command_pre"].add(function)
            return function

        return decorator

    @staticmethod
    def command_postprocessor():
        """
        注册一个命令后处理钩子
        """

        def decorator(function):
            hook_functions["command_post"].add(function)
            return function

        return decorator

    @staticmethod
    def process_error():
        """
        注册一个错误处理钩子
        """

        def decorator(function):
            hook_functions["process_error"].add(function)
            return function

        return decorator

    @staticmethod
    async def startup():
        if cors := [startup(**inject(None, startup)) for startup in hook_functions["startup"]]:  # noqa
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[startup]: {type(exception)}: {exception}")

    @staticmethod
    async def shutdown():
        if cors := [shutdown(**inject(None, shutdown)) for shutdown in hook_functions["shutdown"]]:  # noqa
            try:
                await asyncio.gather(*cors)
            except Exception as exception:
                logs.info(f"[shutdown]: {type(exception)}: {exception}")

    @staticmethod
    async def command_pre(message: Message):
        if cors := [pre(**inject(message, pre)) for pre in hook_functions["command_pre"]]:  # noqa
            try:
                await asyncio.gather(*cors)
            except StopPropagation as e:
                raise StopPropagation from e
            except Exception as exception:
                logs.info(f"[command_pre]: {type(exception)}: {exception}")

    @staticmethod
    async def command_post(message: Message):
        if cors := [post(**inject(message, post)) for post in hook_functions["command_post"]]:  # noqa
            try:
                await asyncio.gather(*cors)
            except StopPropagation as e:
                raise StopPropagation from e
            except Exception as exception:
                logs.info(f"[command_post]: {type(exception)}: {exception}")

    @staticmethod
    async def process_error_exec(message: Message, command, exc_info: BaseException, exc_format: str):
        cors = []
        try:
            for error in hook_functions["process_error"]:
                try:
                    data = inject(message, error, command=command, exc_info=exc_info, exc_format=exc_format)
                except Exception as exception:
                    logs.info(f"[process_error]: {type(exception)}: {exception}")
                    continue
                cors.append(error(**data))  # noqa
            if cors:
                await asyncio.gather(*cors)
        except SystemExit:
            await Hook.shutdown()
            sys.exit(0)
        except StopPropagation as e:
            raise StopPropagation from e
        except Exception as exception:
            logs.info(f"[process_error]: {type(exception)}: {exception}")
