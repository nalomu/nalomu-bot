import asyncio
from functools import wraps
from typing import List, Callable, Awaitable, Union, Iterable

import nonebot

from nalomu import send_msg_to_group

listener_list: List[Callable[[], Awaitable]] = []
bot = nonebot.get_bot()
run_alive = False


def call_on_api_available(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        return f(*args, **kwargs)

    listener_list.append(f)
    return decorated


@bot.on_meta_event('lifecycle')
async def bot_api_available(commandSession):
    global run_alive
    if len(listener_list) and not run_alive:
        await asyncio.gather(*[f() for f in listener_list], loop=bot.loop)
        run_alive = False


@call_on_api_available
async def bot_start_notify():
    from nalomu.orm import Group, SessionManager, Mixin
    from config import NICKNAME
    msg = NICKNAME[0] + '重启了！'
    with SessionManager() as session:
        groups: Iterable[Union[Group, Mixin]] = Group.select(session=session, restart_notify=1)
        await asyncio.gather(*[send_msg_to_group(group_id=group.group_number, msg=msg)
                               for group in groups])
