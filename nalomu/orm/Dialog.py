from sqlalchemy import Column, String, Integer, DateTime, SmallInteger, ForeignKey
from sqlalchemy.orm import relationship

from nalomu.orm import Base, Mixin, User


class Dialog(Base, Mixin):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    command = Column(String(191), index=True)
    result = Column(String(191))
    user_id = Column(Integer, ForeignKey('users.id'), index=True)
    user: User = relationship('User', lazy='joined')
    is_regex = Column(SmallInteger)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
            self,
            command=None,
            result=None,
            user_qq=None,
            is_regex=0,
    ):
        self.score = None
        self.command = command
        self.result = result

        self.user_id = user_qq
        self.is_regex = is_regex
