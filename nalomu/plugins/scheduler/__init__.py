import asyncio

import nonebot
import pytz
from aiocqhttp.exceptions import Error as CQHttpError
from nonebot import CommandSession
from nonebot.argparse import ArgumentParser
from nonebot.command.argfilter.controllers import handle_cancellation

from config import SUPERUSERS
from nalomu.orm import SessionManager
from nalomu.plugins.user import NUser
from .data_source import add_cron_job, remove_job, get_jobs, send_msg, send_user_goodmorning, send_user_goodnight, \
    get_all_jobs, send_group_time, send_group_goodmorning, send_group_goodnight, switch_group
from nalomu.orm.Schedules import Schedules

logger = nonebot.logger
__plugin_name__ = '每日提醒'
__plugin_usage__ = r"""
schedule_add/sa/添加提醒 使用 -h 查看完整帮助
schedule_list/sl/提醒列表 [-a --all]: 查看自己在本群/私聊设置的提醒 
    -a --all 查看自己设置的全部提醒
schedule_remove/sr/移除提醒 [-i --id] [任务名]: 后发送任务名移除任务
    -i --id 使用id指定任务
schedule_all_list/sal: 查看所有任务（需要SUPERUSER权限）
切换[早/晚]安开关: 切换每天[早上7点/晚上23点]的私聊信息开关
hour_alarm_group/hag/群开关整点报时和早晚安报时: 开启群每天早上7点和晚上23点的早晚安和每小时报时
""".strip()


@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    """
    每小时报时
    """
    try:
        await send_group_time()
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job('cron', hour=7, timezone=pytz.timezone('Asia/Shanghai'))
async def _():
    """
    早上好
    """
    try:
        await send_group_goodmorning()
        await send_user_goodmorning()
    except CQHttpError:
        pass


@nonebot.scheduler.scheduled_job('cron', hour=23, timezone=pytz.timezone('Asia/Shanghai'))
async def _():
    """
    晚安
    """
    try:
        await send_group_goodnight()
        await send_user_goodnight()
    except CQHttpError:
        pass


@nonebot.on_command('schedule_add', aliases=('sa', '添加提醒',), shell_like=True)
async def schedule_add(session: CommandSession):
    """
    添加一个每日定时提醒，Asia/Shanghai时区
    :return:
    """
    ttype = 'cron'
    usage = r"""
添加提醒

使用方法：
    添加提醒 [OPTIONS]
    schedule_add [OPTIONS]
    sa [OPTIONS]

OPTIONS：
    -h, --help  显示本使用帮助
    -o, --hours HOURS 小时
    -m, --minutes MINUTES 分钟
    -j, --job_name JOB_NAME 任务名
    --at_sender at发送者
    --msg MSG 要发送的消息
""".strip()
    parser = ArgumentParser(session=session, usage=usage)
    parser.add_argument('-o', '--hours', help='小时')
    parser.add_argument('-m', '--minutes', help='分钟')
    parser.add_argument('-j', '--job_name', help='任务名')
    parser.add_argument('--at_sender', action='store_const', help='at发送者', const='y')
    parser.add_argument('--msg', help='要发送的消息')
    args = parser.parse_args(session.argv)
    hours = int(args.hours if (args.hours is not None)
                else session.get('hours', prompt='小时（0-23）',
                                 arg_filters=[handle_cancellation(session), ]  # 处理用户可能的取消指令
                                 ))
    if hours > 23 or hours < 0:
        await session.send('小时只能是0-23的整数')
        return

    minutes = int(args.minutes if (args.minutes is not None)
                  else session.get('minutes', prompt='分钟（0-59）',
                                   arg_filters=[handle_cancellation(session), ]  # 处理用户可能的取消指令
                                   ))
    if minutes > 59 or minutes < 0:
        await session.send('分钟只能是0-59的整数')
        return

    msg = (args.msg if (args.msg is not None)
           else session.get('msg', prompt='发送要发的消息',
                            arg_filters=[handle_cancellation(session), ]  # 处理用户可能的取消指令
                            ))

    user_id = session.ctx['user_id']
    user_id = (await NUser.get(user_id)).nuid
    stype = 0 if 'group_id' in session.ctx else 1
    group_id = '' if stype else session.ctx['group_id']

    at_sender = (args.at_sender if (args.at_sender is not None)
                 else session.get('at_sender', prompt='是否需要at任务添加人(y/n)',
                                  arg_filters=[handle_cancellation(session), ]  # 处理用户可能的取消指令
                                  ))
    logger.debug('at_sender: ' + str(at_sender))
    at_sender = at_sender.lower() == 'y'
    logger.debug('at_sender: ' + str(at_sender))
    job_name = (args.job_name if (args.job_name is not None)
                else session.get('job_name', prompt='计划任务名',
                                 arg_filters=[handle_cancellation(session), ]  # 处理用户可能的取消指令
                                 ))

    await add_cron_job(group_id=group_id,
                       send_type=stype,
                       msg=msg,
                       at_sender=at_sender,
                       user_id=user_id,
                       trigger=ttype,
                       hours=hours,
                       minutes=minutes,
                       job_name=job_name)
    await session.send('ok')


@nonebot.on_command('schedule_remove', aliases=('sr', '移除提醒',))
async def schedule_remove(session: CommandSession):
    """
    移除提醒
    :param CommandSession session:会话对象
    :return:
    """
    user_id = session.ctx['user_id']
    user_id = (await NUser.get(user_id)).nuid
    if 'id' in session.state:
        ids = session.get('id')
        res = await remove_job('', user_id, ids=ids)
        job_name = f'id={ids}'
    else:
        job_name = session.get('job_name', prompt='计划任务名')
        res = await remove_job(job_name, user_id)
    if res:
        await session.send(f'成功删除计划任务 {job_name}')
    else:
        await session.send(f'没有找到计划任务 {job_name}，请检查你的输入是否正确')


@schedule_remove.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['job_name'] = stripped_arg
            args = stripped_arg.split(' ')
            if (args[0] == '--id' or args[0] == '-i') and len(args) >= 2:
                session.state['id'] = stripped_arg
        return
    session.state[session.current_key] = stripped_arg


@nonebot.on_command('schedule_list', aliases=('sl', '提醒列表',))
async def schedule_list(session: CommandSession):
    user_id = session.ctx['user_id']
    user_id = (await NUser.get(user_id)).nuid
    group_id = 'group_id' in session.ctx and session.ctx['group_id']
    is_all = 'is_all' in session.state and session.state['is_all']
    with SessionManager() as db_session:
        jobs = await get_jobs(user_id, group_id, is_all, db_session)

        if len(jobs) == 0:
            await session.send(f'还没有添加过提醒')
            return

        for job in jobs:
            await session.send(job.job_name)
            await asyncio.sleep(0.8)
        await session.send(f'以上是所有的 {len(jobs)} 个提醒')


@schedule_list.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg == '-a' or stripped_arg == '--all':
            session.state['is_all'] = True


@nonebot.on_command('schedule_all_list', aliases=('sal',))
async def schedule_all_list(session: CommandSession):
    user_id = session.ctx['user_id']
    if user_id not in SUPERUSERS:
        await session.send(f'权限不足')
        return
    jobs = await get_all_jobs()

    if len(jobs) == 0:
        await session.send(f'还没有添加过提醒')
        return

    for job in jobs:
        await session.send(f'{job.id} -- {job.job_name}')
        await asyncio.sleep(0.8)
    await session.send(f'以上是所有的 {len(jobs)} 个提醒')


@nonebot.on_command('hour_append_group', aliases=('hag', '群开关整点报时和早晚安报时'))
async def hour_alarm_group(session: CommandSession):
    group_id = session.ctx['group_id'] if 'group_id' in session.ctx else None
    if group_id:
        flag = switch_group(group_id)
        await session.send("开" if flag else "关")
    else:
        await session.send("只支持群, 私聊请用 切换[早/晚]安开关")


def init():
    with SessionManager() as session:
        for s in Schedules.select(session=session):
            assert isinstance(s, Schedules)
            args = (s.group_id, s.send_type, s.msg, s.at_sender, s.user_id)
            nonebot.scheduler.add_job(send_msg,
                                      trigger=s.type,
                                      args=args,
                                      timezone=pytz.timezone('Asia/Shanghai'),
                                      hour=s.hour,
                                      minute=s.minute,
                                      id=s.job_id)


init()
