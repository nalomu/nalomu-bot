import math
import pytz
import random
from datetime import datetime, timedelta
from nonebot import logger

from nalomu.config_loader import config
from nalomu.orm import Session, User, UserPointLog
from async_property import async_property

try:
    import ujson as json
except ImportError:
    import json

fortune_list = {
    "大吉": "",
    "吉": "",
    "中吉": "",
    "小吉": "",
    "半吉": "",
    "末吉": "",
    "末小吉": "",
    "平": "",
    "凶": "",
    "小凶": "",
    "半凶": "",
    "末凶": "",
    "大凶": "",
}


# fortune_list = {'大吉': "运势大好",
#                 '吉': "运势不错",
#                 '小吉': "小吉炖蘑菇",
#                 '无': "无中生有（）",
#                 '小凶': "不要灰心，贫乳即正义（）",
#                 '凶': "不要灰心，下次再来（）",
#                 '大凶': "不要灰心，多喝热水（）"}


class NUser:
    def __init__(self, user_id):
        logger.debug(f'NUser({user_id}) init')
        self.session = Session()
        # 是 coolq 的 user_id ，实际上是 qq 号
        self.user_id = user_id
        self._user: User = User.first(qq=self.user_id, session=self.session)
        self.nuid = self._user.id if self._user else None

    def __del__(self):
        logger.debug(f'NUser({self.user_id}) del')
        self.session.close()

    @async_property
    async def user(self) -> User:
        if not self._user:
            self._user = await User.get(qq=self.user_id,
                                        session=self.session)
        return self._user

    @classmethod
    async def get(cls, qq):
        return cls(qq)

    @async_property
    async def name(self):
        return (await self.user).name

    async def set_name(self, name: str):
        user = (await self.user)
        user.name = name
        user.save(session=self.session)
        return True

    async def set_gmf(self):
        user = (await self.user)
        user.gmf = not bool(user.gmf)
        flag = user.gmf
        user.save(session=self.session)
        return flag

    async def set_gnf(self):
        user = (await self.user)
        user.gnf = not bool(user.gnf)
        flag = user.gnf
        user.save(session=self.session)
        return flag

    @async_property
    async def point(self):
        return (await self.user).point

    @async_property
    async def continuous_checkin(self):
        return (await self.user).continuous_checkin

    @async_property
    async def high_continuous_checkin(self):
        return (await self.user).high_continuous_checkin

    @async_property
    async def hcc(self):
        return await self.high_continuous_checkin

    @async_property
    async def cc(self):
        return await self.cc

    @async_property
    async def fortune(self):
        fortune = await self.checkin()
        if fortune:
            checkin = True
        else:
            checkin = False
            fortune = (await self.user).fortune
        return checkin, fortune

    async def checkin(self):
        # 只要天数
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        fmt = '%Y%m%d'
        now_date = datetime.strptime(now.strftime(fmt), fmt)
        user = (await self.user)
        if not user.last_checkin:
            flag = True
            date_diff = timedelta(0)
        else:
            last_checkin_date = datetime.strptime(user.last_checkin.strftime(fmt), fmt)
            date_diff = now_date - last_checkin_date

            if date_diff >= timedelta(days=1):
                flag = True
            else:
                flag = False
        if flag:
            # 如果间隔刚好是一天
            if date_diff == timedelta(days=1):
                user.continuous_checkin += 1

            # 断签
            else:
                user.checked_bonus = 0
                user.continuous_checkin = 1

            # 超过了最高签到天数
            if not user.high_continuous_checkin or user.continuous_checkin >= user.high_continuous_checkin:
                user.high_continuous_checkin = user.continuous_checkin

            # 保存最后一次签到的北京时间
            user.last_checkin = now

            # 保存今日运势
            user.fortune = random.choice(list(fortune_list.keys()))
            fortune = user.fortune

            # 重置绑签状态
            user.musubitsuke = False

            # 积分+10
            user.change_point(10, '签到', UserPointLog.TypeEnum.checkin)

            # 保存，对数据库进行操作
            user.save(session=self.session)
            return fortune
        else:
            return False

    async def musubitsuke(self):
        user = await self.user
        if not user.last_checkin:
            return 2
        elif not user.musubitsuke:
            user.musubitsuke = True
            user.save(session=self.session)
            return 0
        else:
            return 1

    async def slap(self):
        user = await self.user
        if user.point < 1:
            return False
        else:
            user.change_point(-1, '鼓掌', UserPointLog.TypeEnum.slap)
            user.save(session=self.session)
            return True

    async def bonus(self):
        user = await self.user
        bonus = {'normal': 0, 'highest': 0}
        bcc = self.cc - (user.checked_bonus or 0)
        bhcc = self.hcc - (user.checked_high_bonus or 0)
        bonus['normal'] = math.floor(bcc / 5) * 3
        bonus['highest'] = math.floor(bhcc / 5) * 5
        changed = bonus['normal'] + bonus['highest']
        user.change_point(changed, '奖励', UserPointLog.TypeEnum.bonus)
        user.checked_bonus = self.cc - self.cc % 5
        user.checked_high_bonus = self.hcc - self.hcc % 5
        user.save(session=self.session)
        return bonus
