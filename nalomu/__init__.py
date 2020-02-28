import asyncio
import math
from nonebot.typing import Context_T, Message_T


async def _send(ctx: Context_T, msg: Message_T, at_sender=False):
    from nonebot import get_bot
    await asyncio.sleep(math.log10(len(msg)))
    await get_bot().send(ctx, msg, at_sender=at_sender)


async def _send_to_user(user_id, msg: Message_T):
    from nonebot import get_bot
    await get_bot().send_private_msg(user_id=user_id, message=msg)


async def send_msg_auto_delay(ctx: Context_T, msg: Message_T, at_sender=False):
    asyncio.ensure_future(_send(ctx, msg, at_sender))


async def send_msg_to_user(user_id, msg: Message_T):
    from nonebot import get_bot
    await get_bot().send_private_msg(user_id=user_id, message=msg)


async def send_msg_to_group(group_id, msg: Message_T):
    from nonebot import get_bot
    await get_bot().send_group_msg(group_id=group_id, message=msg)


from nalomu.util import NDict
# from nalomu import commands
# from nalomu.init import call_on_api_available
