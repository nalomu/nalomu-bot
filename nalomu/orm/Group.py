from typing import Iterable, Union

import nonebot
from sqlalchemy import Column, String, Integer, DateTime, SmallInteger, BigInteger

from nalomu.plugins import call_on_api_available
from nalomu.orm import Base, Mixin, SessionManager


class Group(Base, Mixin):
    __tablename__ = 'groups'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    group_number = Column(BigInteger, index=True)
    hourly_clock = Column(SmallInteger)
    good_night = Column(SmallInteger)
    good_morning = Column(SmallInteger)
    restart_notify = Column(SmallInteger)
    in_group_msg = Column(String(191))
    welcome_msg = Column(String(191))
    welcome_at_member = Column(SmallInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self,
                 group_number,
                 hourly_clock=0,
                 good_night=0,
                 good_morning=0,
                 in_group_msg='',
                 welcome_msg='',
                 welcome_at_member=0,
                 restart_notify=0,
                 ):
        self.group_number = group_number
        self.hourly_clock = hourly_clock
        self.good_night = good_night
        self.good_morning = good_morning
        self.in_group_msg = in_group_msg
        self.welcome_msg = welcome_msg
        self.welcome_at_member = welcome_at_member
        self.restart_notify = restart_notify


@call_on_api_available
async def init_group():
    group_list = await nonebot.get_bot().get_group_list()
    group_ids = set([group['group_id'] for group in group_list])
    with SessionManager() as session:
        exists_group: Iterable[Union[Group, Mixin]] = Group.select(session=session)
        database_group_ids = set([group.group_number for group in exists_group])
        diff_groups = group_ids - database_group_ids
        for group_id in diff_groups:
            Group(group_id).save(session=session)
