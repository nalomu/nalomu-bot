import asyncio

from nalomu.commands import BaseCommand, method_command, method_parser
from nalomu.plugins.user import NUser
from .data_source import get_memorandum, add_memorandum, del_memorandum, remind_memorandum


class MemorandumCommands(BaseCommand):

    @method_command('memorandum_list', aliases=('备忘录',))
    async def memorandum_list(self):
        user_id = self.user_id
        res = await get_memorandum((await NUser.get(user_id)).nuid)
        if len(res) == 0:
            await self.send('备忘录是空的')
            return
        elif len(res) >= 10 and self.group_id:
            await self.send('条目过多，请私聊')
            return
        for idx, val in enumerate(res, 1):
            await self.send(f'{idx}: {val.title}' +
                            (f'\n    {val.content}'
                             if val.content
                             else ''), no_delay=True)
            await asyncio.sleep(0.8)

    @method_command('memorandum_del', aliases=('删除备忘录',))
    async def memorandum_del(self):
        user_id = self.user_id
        title = self.get('title', prompt='标题')
        await del_memorandum((await NUser.get(user_id)).nuid, title)
        await self.send('ok')

    @method_command('memorandum_del_all', aliases=('清空备忘录',))
    async def memorandum_del_all(self):
        user_id = self.user_id
        await del_memorandum((await NUser.get(user_id)).nuid)
        await self.send('ok')

    @method_command('memorandum_add', aliases=('添加备忘录',))
    async def memorandum_add(self):
        user_id = self.user_id
        title = self.get('title', prompt='标题')
        content = self.get('content', prompt='内容')
        await add_memorandum((await NUser.get(user_id)).nuid, title, content)
        await self.send('ok')

    @method_command('memorandum_remind', aliases=('备忘录提醒',))
    async def memorandum_remind(self):
        return
        user_id = self.user_id
        title = self.get('title', prompt='标题')
        await remind_memorandum((await NUser.get(user_id)).nuid, title)
        await self.send('ok')

    @memorandum_add.args_parser
    @memorandum_del.args_parser
    @memorandum_list.args_parser
    @memorandum_remind.args_parser
    @method_parser
    async def _(self):
        stripped_arg = self.stripped_msg

        if self.session.is_first_run:
            if stripped_arg:
                args = stripped_arg.split('##')
                self.session.state['title'] = args[0]
                if len(args) > 1:
                    self.session.state['content'] = args[1]
                elif len(args) == 1:
                    self.session.state['content'] = ''
            return
        self.session.state[self.session.current_key] = stripped_arg


__all__ = ['MemorandumCommands']
