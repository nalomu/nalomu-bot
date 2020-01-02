from datetime import datetime
from typing import Iterable, Dict

import pytz

from nalomu.orm import Session_T


class Mixin(object):
    __tablename__ = None
    __table_args__ = {'extend_existing': True}

    def save(self, *, session: Session_T) -> bool:
        if hasattr(self, 'updated_at'):
            setattr(self, 'updated_at', datetime.now(pytz.timezone('Asia/Shanghai')))
        if hasattr(self, 'created_at') and not getattr(self, 'created_at'):
            setattr(self, 'created_at', datetime.now(pytz.timezone('Asia/Shanghai')))
        session.add(self)
        session.commit()
        return True

    def delete(self, *, session: Session_T) -> bool:
        session.delete(self)
        session.commit()
        return True

    @classmethod
    def select(cls, *, session: Session_T, **where) -> Iterable['Mixin']:
        q = session.query(cls)
        if len(where) > 0:
            q = q.filter_by(**where)
        rs = q.all()
        return rs

    @classmethod
    def first(cls, *, session: Session_T, **where) -> 'Mixin':
        q = session.query(cls)
        if len(where) > 0:
            q = q.filter_by(**where)
        rs = q.first()
        return rs

    @classmethod
    def update(cls, data, *, session: Session_T, where: Dict = None) -> int:
        q = session.query(cls)
        if where:
            q = q.filter_by(**where)
        row = q.update(data)
        session.commit()
        return row

    @classmethod
    def delete_all(cls, *, session: Session_T, **where) -> int:
        if not where:
            raise Exception('don\'t do that!')
        row = session.query(cls).filter_by(**where).delete()
        session.commit()
        return row

    def __repr__(self) -> str:
        return '{\n\t' + ('\n\t'.join([
            f'{attr}:{str(getattr(self, attr))}'
            for attr in filter(lambda x: not x.startswith('_'), self.__dict__)
        ])) + '\n}'

    def __str__(self) -> str:
        return self.__repr__()
