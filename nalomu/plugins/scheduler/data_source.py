import asyncio
import json
import os
import random
import string
import nonebot
import pytz

from datetime import datetime
from apscheduler.jobstores.base import JobLookupError

from nalomu.orm import Schedules, User, SessionManager, Session_T

dirname = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(dirname) or not os.path.isdir(dirname):
    os.makedirs(dirname)

jsonfile = os.path.join(dirname, 'groups.json')
groups = []


def init():
    global groups
    if os.path.exists(jsonfile):
        with open(jsonfile, encoding='utf-8') as f:
            groups = json.loads(f.read())
    else:
        with open(jsonfile, 'w', encoding='utf-8') as f:
            groups = []
            f.write(json.dumps(groups))


init()


def random_str(n):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))


async def add_cron_job(group_id=None,
                       send_type=None,
                       msg=None,
                       at_sender=None,
                       user_id=None,
                       trigger=None,
                       hours=None,
                       minutes=None,
                       job_name=None):
    args = (group_id, send_type, msg, at_sender, user_id)
    job_id = str(user_id) + '_' + random_str(8)
    nonebot.scheduler.add_job(send_msg,
                              trigger=trigger,
                              args=args,
                              timezone=pytz.timezone('Asia/Shanghai'),
                              hour=hours,
                              minute=minutes,
                              id=job_id)
    with SessionManager() as session:
        Schedules(group_id=group_id,
                  job_id=job_id,
                  job_name=job_name,
                  send_type=send_type,
                  user_id=user_id,
                  type_=trigger,
                  hour=hours,
                  minute=minutes,
                  msg=msg,
                  at_sender=at_sender).save(session=session)


async def remove_job(jname, user_id, ids=None):
    with SessionManager() as session:
        if ids is not None:
            s = Schedules.first(session=session, id=ids, user_id=user_id)
        else:
            s = Schedules.first(session=session, job_name=jname, user_id=user_id)
        if s is None:
            return False
        try:
            nonebot.scheduler.remove_job(s.job_id)
            s.delete(session=session)
            return True
        except JobLookupError:
            return False


async def get_jobs(user_id, group_id, is_all, session: Session_T):
    payload = {
        "user_id": user_id,
    }
    if not is_all:
        if group_id:
            payload.update({"group_id": group_id})
        else:
            payload.update({"group_id": ""})

    return Schedules.select(session=session, **payload)


async def get_all_jobs():
    with SessionManager() as session:
        return Schedules.select(session=session)


async def send_msg(group_id, send_type, msg, at_sender, user_id):
    args = locals()
    bot = nonebot.get_bot()
    nonebot.logger.debug(f'send_msg:\n\t{args}')
    with SessionManager() as session:
        user_id = User.first(session=session, id=user_id).qq
    try:
        if send_type == 0:
            #     group_id = Group.first(id=group_id).group_number
            msg = (f'[CQ:at,qq={user_id}]' if at_sender else '') + msg
            await bot.send_group_msg(group_id=group_id,
                                     message=msg)
        elif send_type == 1:
            await bot.send_private_msg(user_id=user_id, message=msg)
    except nonebot.CQHttpError:
        pass


async def send_user_goodmorning():
    with SessionManager() as session:
        users = User.select(session=session, gmf=1)
    for user in users:
        assert isinstance(user, User)
        msg = user.name + '，早上好~~~~' if user.name else '早上好~~~~'
        asyncio.ensure_future(send_msg(group_id=None,
                                       send_type=1,
                                       msg=msg,
                                       at_sender=False,
                                       user_id=user.qq))


async def send_user_goodnight():
    with SessionManager() as session:
        users = User.select(session=session, gnf=1)
    for user in users:
        assert isinstance(user, User)
        msg = user.name + '，晚安~~~~' if user.name else '晚安~~~~'
        asyncio.ensure_future(send_msg(group_id=None,
                                       send_type=1,
                                       msg=msg,
                                       at_sender=False,
                                       user_id=user.qq))


async def send_group_time():
    """
    向已注册的群里发送整点报时
    :return:
    """
    bot = nonebot.get_bot()
    now = datetime.now(pytz.timezone('Asia/Shanghai'))
    for group in groups:
        asyncio.ensure_future(bot.send_group_msg(group_id=group,
                                                 message=f'现在北京时间{now.hour}点整啦！'))


async def send_group_goodmorning():
    """
    向已注册的群里发送早上好
    :return:
    """
    bot = nonebot.get_bot()
    msg = '早上好~今天也是援气满满的一天呢！'
    for group in groups:
        asyncio.ensure_future(bot.send_group_msg(group_id=group,
                                                 message=msg))


async def send_group_goodnight():
    """
    向已注册的群里发送晚安
    :return:
    """
    bot = nonebot.get_bot()
    msg = '晚安~今天也是充实的一天呢！'
    for group in groups:
        asyncio.ensure_future(bot.send_group_msg(group_id=group,
                                                 message=msg))


def switch_group(group_id: int):
    if group_id in groups:
        groups.remove(group_id)
        flag = False
    else:
        groups.append(group_id)
        flag = True
    with open(jsonfile, 'w', encoding='utf-8') as f:
        f.write(json.dumps(groups))
    return flag
