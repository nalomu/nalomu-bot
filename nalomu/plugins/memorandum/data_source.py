from nalomu.orm import Memorandum, SessionManager


async def get_memorandum(user_id):
    with SessionManager() as session:
        return Memorandum.select(session=session, user_id=user_id)


async def add_memorandum(user_id, title='', content=''):
    with SessionManager() as session:
        Memorandum(user_id, title, content).save(session=session)


async def del_memorandum(user_id, title=''):
    with SessionManager() as session:
        if title:
            return Memorandum.first(
                session=session,
                user_id=user_id,
                title=title
            ).delete(session=session)
        else:
            return Memorandum.delete_all(session=session, user_id=user_id)


async def remind_memorandum(user_id, title=''):
    pass
