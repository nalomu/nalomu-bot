from functools import wraps
from typing import Callable, Iterable, Union, Optional, Any, Awaitable, Type, Dict

from nonebot import CommandSession, NLPSession, on_natural_language, logger, on_command
from nonebot.command import Command
from nonebot.typing import CommandName_T
from nonebot import permission as perm

from nalomu.commands import BaseCommand
from nalomu.util import get_class_that_defined_method

MethodCommand_T = Callable[[BaseCommand], Awaitable[Any]]


def method_command(name: Union[str, CommandName_T], *,
                   aliases: Iterable[str] = (),
                   permission: int = perm.EVERYBODY,
                   only_to_me: bool = True,
                   privileged: bool = False,
                   shell_like: bool = False,
                   need_bot_open: bool = False) -> Callable:
    def deco(func: MethodCommand_T) -> Callable:
        @wraps(func)
        async def wrapped_function(session: CommandSession):
            from config import BOT_SWITCH, NICKNAME
            logger.info(need_bot_open)
            logger.info(BOT_SWITCH)
            if need_bot_open and not BOT_SWITCH:
                await session.send(NICKNAME[0] + '没有打开')
                return

            cls = get_class_that_defined_method(func)
            if not cls:
                raise Exception('cannot resolve class from method')
            return await func(cls(session))

        wrapped_function.is_command = True
        return on_command(name,
                          aliases=aliases,
                          permission=permission,
                          only_to_me=only_to_me,
                          privileged=privileged,
                          shell_like=shell_like)(wrapped_function)

    return deco


def method_parser(func: MethodCommand_T) -> Callable:
    @wraps(func)
    async def wrapped_function(session: CommandSession):
        cls = get_class_that_defined_method(func)
        if not cls:
            raise Exception('Cannot resolve class from method.')
        instance = cls(session)
        if not isinstance(instance, BaseCommand):
            raise Exception('This method is not from a subclass of BaseCommand')
        return await func(instance)

    return wrapped_function


def method_nlp(keywords: Union[Optional[Iterable], Callable] = None,
               *, permission: int = perm.EVERYBODY,
               only_to_me: bool = True,
               only_short_message: bool = True,
               allow_empty_message: bool = False) -> Callable:
    func_get_args = locals()

    def deco(func: Callable):
        @wraps(func)
        async def wrapped_function(session: NLPSession):
            cls = get_class_that_defined_method(func)
            if not cls:
                raise Exception('cannot resolve class from method')
            return await func(cls(session))

        return on_natural_language(**func_get_args)(wrapped_function)

    if isinstance(keywords, Callable):
        # here "keywords" is the function to be decorated
        return method_nlp()(keywords)
    else:
        return deco


__all__ = ['method_command', 'method_parser', 'method_nlp']
