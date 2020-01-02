from sqlalchemy import Column, String, Integer, Text, BigInteger, DateTime, SmallInteger

from nalomu.orm import Base, Mixin

"""
SQLAlchemy 通过 Column 这个描述器类来替换数据库字段的访问和赋值过程
"""


class Schedules(Base, Mixin):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    group_id = Column(Integer)
    job_id = Column(String(191))
    job_name = Column(String(191))
    user_id = Column(BigInteger)
    send_type = Column(Integer)
    type = Column(Integer, index=True)
    hour = Column(Integer)
    minute = Column(Integer)
    msg = Column(Text)
    at_sender = Column(SmallInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self,
                 group_id,
                 job_id, job_name,
                 send_type,
                 user_id,
                 type_,
                 hour,
                 minute,
                 msg,
                 at_sender,
                 ):
        self.group_id = group_id
        self.job_id = job_id
        self.job_name = job_name
        self.send_type = send_type
        self.user_id = user_id
        self.type = type_
        self.hour = hour
        self.minute = minute
        self.msg = msg
        self.at_sender = at_sender
