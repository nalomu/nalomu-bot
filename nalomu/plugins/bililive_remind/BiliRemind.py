import nonebot

from nalomu.orm import LiveListen, SessionManager
from nalomu.orm.LiveListen import type_group, type_user
from . import NBiliBiliLive

logger = nonebot.logger


class BiliRemind:
    def __init__(self, room_id, group_id=None, user_id=None):
        self.listen_groups = set()
        self.listen_users = set()
        self.status = False
        if isinstance(room_id, LiveListen):
            livel = room_id
            self.room_id = livel.room_id
            if livel.type == type_group:
                self.append_group(livel.to_id, add_in_database=False)
            elif livel.type == type_user:
                self.append_user(livel.to_id, add_in_database=False)
        else:
            self.room_id = room_id
        if group_id:
            self.append_group(group_id)
        if user_id:
            self.append_user(user_id)

    def __await__(self):
        return self._async_init().__await__()

    async def _async_init(self):
        self.nlive: NBiliBiliLive = await NBiliBiliLive(self.room_id)
        return self

    def append_group(self, group_id, add_in_database=True) -> bool:
        if group_id not in self.listen_groups:
            self.listen_groups.add(group_id)
            if add_in_database:
                logger.info(f'add to database [room_id:{self.room_id}, group_id:{group_id}]')
                with SessionManager() as session:
                    LiveListen(group_id, self.room_id, type_group).save(session=session)

            return True
        return False

    def append_user(self, user_id, add_in_database=True) -> bool:
        if user_id not in self.listen_users:
            self.listen_users.add(user_id)
            if add_in_database:
                logger.info(f'add to database [room_id:{self.room_id}, user_id:{user_id}]')
                with SessionManager() as session:
                    LiveListen(user_id, self.room_id, type_user).save(session=session)
            return True
        return False

    def remove_group(self, gid):
        if gid in self.listen_groups:
            self.listen_groups.remove(gid)
            where = dict(room_id=self.room_id, to_id=gid, type=type_group)
            with SessionManager() as session:
                LiveListen.first(session=session, **where).delete(session=session)
            return True
        return False

    def remove_user(self, uid):
        if uid in self.listen_users:
            self.listen_users.remove(uid)
            where = dict(room_id=self.room_id, to_id=uid, type=type_user)
            with SessionManager() as session:
                LiveListen.first(session=session, **where).delete(session=session)
            return True
        return False

    def has_user(self, user_id):
        return user_id in self.listen_users

    def has_group(self, group_id):
        return group_id in self.listen_groups

    async def check_send(self):
        bot = nonebot.get_bot()
        info = await self.nlive.get_room_info()
        if info['status'] != self.status:
            s = '[ https://live.bilibili.com/{} ]-[{}]({}) {} '.format(
                str(self.room_id),
                info["hostname"],
                '开播' if info['status'] else '下播',
                info['roomname'])
            for group_id in self.listen_groups:
                try:
                    await bot.send_group_msg(group_id=group_id, message=s)
                except nonebot.CQHttpError:
                    pass
            for user_id in self.listen_users:
                try:
                    await bot.send_private_msg(user_id=user_id, message=s)
                except nonebot.CQHttpError:
                    pass
            self.status = info['status']

    async def check_room(self):
        return await self.nlive.check_room()

    async def get_format_info(self):
        info = await self.nlive.get_room_info()
        return '[ https://live.bilibili.com/{} ]-[{}]({}) {} '.format(self.room_id,
                                                                      info["hostname"],
                                                                      '开播' if info['status'] else '未开播',
                                                                      info['roomname'])

    def has(self, group_id, user_id):
        return self.has_group(group_id) if group_id else self.has_user(user_id)
