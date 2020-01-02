from datetime import datetime

import pytz
from nonebot import IntentCommand

from config import SUPERUSERS
from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp

from nalomu.config_loader import config as localconfig

tzs = {
    '北京': 'Asia/Shanghai',
    '东京': 'Asia/Tokyo',
    '纽约': 'America/New_York',
    '洛杉矶': 'America/Los_Angeles',
    '亚利桑那州': 'US/Arizona',
    '伦敦': 'Europe/London',
    '巴黎': 'Europe/Paris',
}


class OtherCommands(BaseCommand):

    @method_command('switch_bot', aliases=('switch_bot', '切换bot开关'))
    async def switch_bot(self):
        if self.user_id not in SUPERUSERS:
            await self.send('权限不足')
            return
        import config
        config.BOT_SWITCH = not config.BOT_SWITCH
        await self.send('开' if config.BOT_SWITCH else '关')

    @method_command('add_super_user', aliases=('添加bot授权用户', 'asu'))
    async def add_super_user(self):
        if self.user_id not in SUPERUSERS:
            await self.send('权限不足')
            return
        user = int(self.get('user', prompt='qq'))
        if user in SUPERUSERS:
            await self.send('已经授权了')
            return
        SUPERUSERS.append(user)
        su: list = localconfig.super_user.copy()
        su.append(user)
        localconfig.super_user = su
        await self.send('ok')

    @method_command('del_super_user', aliases=('删除bot授权用户', 'dsu'))
    async def del_super_user(self):
        if self.user_id not in SUPERUSERS:
            await self.send('权限不足')
            return
        user = int(self.get('user', prompt='qq'))
        while user in SUPERUSERS:
            SUPERUSERS.remove(user)
        su: list = localconfig.super_user.copy()
        while user in su:
            su.remove(user)
        localconfig.super_user = su
        await self.send('ok')

    @add_super_user.args_parser
    @del_super_user.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('user')

    @method_command('time', only_to_me=False, aliases=("时间",))
    async def time(self):
        tz = self.get('timezone', required=False) or '东京'
        if tz in tzs.keys():
            tzname = f' ({tz}时间)'
            tz = tzs[tz]
        elif tz in pytz.all_timezones_set:
            tzname = f' (timezone: {tz})'
        else:
            tzname = ' (东京时间)'
            tz = 'Asia/Tokyo'
        now = datetime.now(pytz.timezone(tz))
        await self.send(now.strftime('%Y-%m-%d %H:%M:%S') + tzname)

    @time.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('timezone')

    @method_nlp(keywords={'时间'}, only_to_me=False)
    async def _(self):
        # 去掉消息首尾的空白符
        stripped_msg = self.stripped_msg
        if stripped_msg.endswith('时间') and stripped_msg[:-2] in tzs:
            return IntentCommand(90, 'time', current_arg=stripped_msg[:-2])


__all__ = ['OtherCommands', 'tzs']
