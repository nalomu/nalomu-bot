import asyncio
from typing import List

import pytz
from nonebot import CommandSession, scheduler

from nalomu.commands import method_command, BaseCommand, method_parser
from nalomu.orm import LiveListen, SessionManager
from nalomu.orm.LiveListen import type_group, type_user
from nalomu.util import is_number
from . import BiliRemind, NBiliBiliLive


class LiveCommands(BaseCommand):
    remind_list: List[BiliRemind] = []
    orm = LiveListen

    def __init__(self, session: CommandSession):
        """
        :param session:
        """
        super().__init__(session)

    @staticmethod
    def find_remind(room_id) -> BiliRemind:
        """
        find exits remind from list or None
        :param room_id:
        :return: remind if found or None
        """
        for r in LiveCommands.remind_list:
            if r.room_id == int(room_id):
                return r

    @method_command('add_live_remind', aliases=('alr', '添加监听的房间'))
    async def add_live_remind(self):
        # get room_id
        room_id = self.get('room_id', prompt='房间id')
        # validate
        if is_number(room_id):
            remind = self.find_remind(room_id)
            # if exits in list
            if remind:
                if remind.has(group_id=self.group_id, user_id=self.user_id):
                    # already in
                    await self.send('已经在监听的列表里了')
                    return
                else:
                    # append
                    if self.group_id:
                        remind.append_group(self.group_id)
                    else:
                        remind.append_user(self.user_id)
            else:
                room_id = int(room_id)
                # check room exits
                nl = await NBiliBiliLive(room_id)
                (suc, msg) = await nl.check_room()
                if not suc:
                    await self.send(msg)
                    return

                # real room_id
                room_id = msg
                if self.group_id:
                    # init by group_id
                    remind = await BiliRemind(room_id, group_id=self.group_id)
                else:
                    # init by user_id
                    remind = await BiliRemind(room_id, user_id=self.user_id)
                # append to listen list
                self.remind_list.append(remind)
                await self.send('ok')
                await remind.check_send()
        else:
            await self.send('输入的好像不是数字哦')

    @method_command('del_live_remind', aliases=('dlr', '删除监听的房间'))
    async def del_live_remind(self):
        room_id = self.get('room_id', prompt='房间id')
        group_id = self.group_id
        user_id = self.user_id
        if is_number(room_id):
            remind = self.find_remind(room_id)
            if remind and (remind.remove_group(group_id) if group_id else remind.remove_user(user_id)):
                await self.send('ok')
            else:
                await self.send('不在列表里')
        else:
            await self.send('输入的好像不是数字哦')

    @method_command('live_listen_list', aliases=('lll', '查看监听的房间'))
    async def live_listen_list(self):
        group_id = self.group_id
        user_id = self.user_id
        if self.has_arg('room_id'):
            room_id = self.get('room_id')
            remind = self.find_remind(room_id)
            if remind:
                info = await remind.get_format_info()
                await self.send(info, no_delay=True)
            else:
                if is_number(room_id):
                    nl = await NBiliBiliLive(int(room_id))
                    (suc, msg) = await nl.check_room()
                    if not suc:
                        await self.send(msg, no_delay=True)
                    else:
                        info = await nl.check()
                        await self.send(info, no_delay=True)
                else:
                    await self.send('输入的好像不是数字哦')
        else:
            for r in self.remind_list:
                if group_id:
                    if r.has_group(group_id):
                        info = await r.get_format_info()
                        await self.send(info, no_delay=True)
                        await asyncio.sleep(0.8)
                elif r.has_user(user_id):
                    info = await r.get_format_info()
                    await self.send(info, no_delay=True)
                    await asyncio.sleep(0.8)

    @del_live_remind.args_parser
    @add_live_remind.args_parser
    @live_listen_list.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('room_id', '房间名不能为空')

    @classmethod
    async def init(cls):
        with SessionManager() as session:
            for live_listen in cls.orm.select(session=session):
                assert isinstance(live_listen, cls.orm)
                remind = cls.find_remind(live_listen.room_id)
                if not remind:
                    cls.remind_list.append(await BiliRemind(live_listen))
                else:
                    if live_listen.type == type_group:
                        remind.append_group(live_listen.to_id, add_in_database=False)
                    elif live_listen.type == type_user:
                        remind.append_user(live_listen.to_id, add_in_database=False)

    @classmethod
    async def check_and_send(cls):
        for remind in cls.remind_list:
            await remind.check_send()


@scheduler.scheduled_job('interval', minutes=1, timezone=pytz.timezone('Asia/Shanghai'))
async def _():
    await LiveCommands.check_and_send()


asyncio.ensure_future(LiveCommands.init())
