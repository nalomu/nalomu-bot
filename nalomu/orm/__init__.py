from contextlib import contextmanager
from os import path

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session as BaseSession

from config import APP_ROOT
from nalomu.config_loader import config

database_configs = config.database
db_path = path.join(APP_ROOT, 'database.db')
engine = create_engine(f'sqlite:///{db_path}', encoding='utf-8', echo=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)
Session_T = BaseSession


@contextmanager
def SessionManager():
    """Provide a transactional scope around a series of operations."""
    session: Session_T = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


from nalomu.orm.Mixin import Mixin
from nalomu.orm.Dialog import Dialog
from nalomu.orm.LiveListen import LiveListen
from nalomu.orm.Memorandum import Memorandum
from nalomu.orm.Schedules import Schedules
from nalomu.orm.Suggestion import Suggestion
from nalomu.orm.User import User, UserPointLog
from nalomu.orm.Group import Group

Base.metadata.create_all(engine)

if __name__ == '__main__':
    def test():
        with SessionManager() as session:
            for _ in Dialog.select(session=session): print(_)
            for _ in LiveListen.select(session=session): print(_)
            for _ in Memorandum.select(session=session): print(_)
            for _ in Schedules.select(session=session): print(_)
            for _ in Suggestion.select(session=session): print(_)
            for _ in User.select(session=session): print(_)
            for _ in Group.select(session=session): print(_)


    test()
