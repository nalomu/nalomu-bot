from typing import Iterable, Union

import nonebot

from config import SUPERUSERS
from nalomu.orm import Suggestion, SessionManager, Mixin


async def append_suggestion(content, user_qq):
    bot = nonebot.get_bot()
    with SessionManager() as session:
        Suggestion(content, user_qq).save(session=session)
    for user in SUPERUSERS:
        try:
            await bot.send_private_msg(
                user_id=user,
                message=f"收到来自[CQ:at,qq={user_qq}]的反馈: {content}")
        except:
            pass
    return True


async def get_suggestions(status=0):
    with SessionManager() as session:
        suggestions: Iterable[Union[Suggestion, Mixin]] = Suggestion.select(session=session, status=status)
        return [
            f"来自[CQ:at,qq={suggestion.user_qq}]的反馈: {suggestion.content}"
            for suggestion in suggestions
        ]


async def check_all_suggestion():
    with SessionManager() as session:
        Suggestion.update(data=dict(status=1),
                          session=session,
                          where=dict(status=0))
    return True
