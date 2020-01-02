from nalomu.commands import BaseCommand, method_command
from nalomu.orm import SessionManager, Group


class GroupCommands(BaseCommand):
    @method_command('switch_restart_notify', aliases=('切换重启提醒',))
    async def switch_restart_notify(self):
        group_number = self.group_id
        if group_number:
            with SessionManager() as database_session:
                group: Group = Group.first(group_number=group_number, session=database_session)
                restart_notify = not bool(group.restart_notify)
                group.restart_notify = int(restart_notify)
                group.save(session=database_session)
            await self.send('开' if restart_notify else '关')
        else:
            await self.send('暂不支持私人')


__all__ = ['GroupCommands']
