from sqlalchemy import Column, String, Integer, Text, DateTime

from nalomu.orm import Base, engine, Mixin

conn = engine.connect()
"""
SQLAlchemy 通过 Column 这个描述器类来替换数据库字段的访问和赋值过程
"""


class Memorandum(Base, Mixin):
    __tablename__ = 'memorandums'
    id = Column(Integer, primary_key=True, autoincrement=True)  # 每一个类都需要主键
    user_id = Column(String(191), index=True)
    title = Column(String(191), index=True)
    content = Column(Text)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    def __init__(self, user_id, title, content):
        self.user_id = user_id
        self.title = title
        self.content = content
