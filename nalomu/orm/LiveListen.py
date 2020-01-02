import enum

from sqlalchemy import Column, Enum, BigInteger, DateTime, Integer

from nalomu.orm import Base, Mixin


class LiveListen(Base, Mixin):
    class TypeEnum(enum.Enum):
        group = 0
        user = 1

    __tablename__ = 'live_listens'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    room_id = Column(BigInteger)
    to_id = Column(BigInteger)
    type = Column(Enum(TypeEnum))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, to_id, room_id, type_):
        self.to_id = to_id
        self.room_id = room_id
        self.type = type_


type_group = LiveListen.TypeEnum.group
type_user = LiveListen.TypeEnum.user
