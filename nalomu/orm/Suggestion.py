from sqlalchemy import Column, String, Integer, BigInteger, DateTime

from nalomu.orm import Base, engine, Mixin

conn = engine.connect()
"""
SQLAlchemy 通过 Column 这个描述器类来替换数据库字段的访问和赋值过程
"""


class Suggestion(Base, Mixin):
    __tablename__ = 'suggestions'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    content = Column(String(191))
    user_qq = Column(BigInteger)
    status = Column(Integer, default=0)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(
            self,
            content=None,
            user_qq=None,
            status=0,
    ):
        self.content = content
        self.user_qq = user_qq
        self.status = status
