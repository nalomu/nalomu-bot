import asyncio

from nonebot import on_command, CommandSession, logger
from config import SUPERUSERS
from .data_source import append_suggestion, get_suggestions, check_all_suggestion

__plugin_name__ = '反馈'
__plugin_usage__ = r"""
suggestion/反馈/建议/提议 [内容] 添加反馈
check_all_suggestion/确认所有反馈/cas (SUPERUSERS only) 
suggestion/反馈列表 (SUPERUSERS only) 
""".strip()


@on_command('suggestion', aliases=('反馈', '建议', '提议'))
async def suggestion(session: CommandSession):
    content = session.get('content', prompt='内容')
    try:
        res = await append_suggestion(content, session.ctx['user_id'])
        if res:
            await session.send('ok')
    except Exception as e:
        logger.error(e)
        await session.send('出错啦!')


@on_command('check_all_suggestion', aliases=('确认所有反馈', 'cas'))
async def check_suggestion(session: CommandSession):
    if session.ctx['user_id'] not in SUPERUSERS:
        await session.send('权限不足')
        return
    # try:
    res = await check_all_suggestion()
    if res:
        await session.send('ok')
    # except:
    #     await session.send('出错啦!')


@on_command('suggestions', aliases=('反馈列表',), shell_like=True)
async def suggestions(session: CommandSession):
    if session.ctx['user_id'] not in SUPERUSERS:
        await session.send('权限不足')
        return
    await session.send('查询中...')
    checked = True if ('checked' in session.state and session.state['checked']) else False
    try:
        if not checked:
            res = await get_suggestions()
        else:
            res = await get_suggestions(1)
        for s in res:
            await session.send(s)
            await asyncio.sleep(0.5)
        await session.send(f'共{len(res)}条')
    except Exception as e:
        logger.error(e)
        await session.send('出错啦!')


@suggestion.args_parser
@suggestions.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    # 第一次运行
    if session.is_first_run:
        if stripped_arg == '-c':
            session.state['checked'] = True
        if stripped_arg:
            session.state['content'] = stripped_arg
        return

    if not stripped_arg:
        session.pause('请输入')

    session.state[session.current_key] = stripped_arg
