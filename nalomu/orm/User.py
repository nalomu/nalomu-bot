import enum
from typing import List

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship

from nalomu.orm import Base, Mixin

"""
SQLAlchemy 通过 Column 这个描述器类来替换数据库字段的访问和赋值过程
"""


class User(Base, Mixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    qq = Column(Integer, index=True)  # 的qq

    gmf = Column(Integer)  # 早安开关
    gnf = Column(Integer)  # 晚安开关

    point = Column(Integer)  # 积分

    name = Column(String(191))  # 自定义称呼

    last_checkin = Column(DateTime)  # 最后一次签到的时间
    fortune = Column(String(191))  # 今日运势
    musubitsuke = Column(Integer)  # 绑签

    continuous_checkin = Column(Integer)  # 连续签到天数
    high_continuous_checkin = Column(Integer)  # 最高连续签到天数

    checked_bonus = Column(Integer)  # 已获取的连签bonus
    checked_high_bonus = Column(Integer)  # 已获取的最高连签bonus

    created_at = Column(DateTime)  # 创建时间
    updated_at = Column(DateTime)  # 更新时间
    point_logs: List['UserPointLog'] = relationship("UserPointLog")  # 积分日志

    @classmethod
    async def get(cls, qq, session=None):
        qq = int(qq)
        u = cls.first(qq=qq, session=session)
        if not u:
            cls(qq=qq).save(session=session)
            u = cls.first(qq=qq, session=session)
        return u

    def change_point(self, change_point, desc, type_):
        before = int(self.point or 0)
        self.point = after = before + change_point
        self.point_logs.append(UserPointLog(
            user_id=self.id,
            score=change_point,
            before=before,
            after=after,
            type_=type_,
            desc=desc,
        ))
        return self


class UserPointLog(Base, Mixin):
    __tablename__ = 'user_point_logs'

    class TypeEnum(enum.Enum):
        checkin = 0
        slap = 1
        chokyo = 2
        bonus = 3
        other = 99

    id = Column(Integer, primary_key=True)  # 每一个类都需要主键
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    score = Column(Integer)
    before = Column(Integer)
    after = Column(Integer)
    type = Column(Enum(TypeEnum))
    describe = Column(String(191))
    created_at = Column(DateTime)  # 创建时间
    updated_at = Column(DateTime)  # 更新时间

    def __init__(self,
                 user_id,
                 score=0,
                 before=0,
                 after=0,
                 type_=TypeEnum.other,
                 desc='',
                 ):
        self.user_id = user_id
        self.score = score
        self.before = before
        self.after = after
        self.type = type_
        self.desc = desc
