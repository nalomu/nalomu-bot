from nonebot import on_notice, NoticeSession, on_request, RequestSession, logger

# 将函数注册为群成员增加通知处理器
from nalomu.config_loader import config
from nalomu.orm import Group, SessionManager

if config.welcome and config.welcome.msg:
    @on_notice('group_increase')
    async def _(session: NoticeSession):
        # 发送欢迎消息
        if session.ctx["user_id"] == 2556468180:
            msg = f'[CQ:at,qq={session.ctx["user_id"]}] 妈你来啦！'
        else:
            msg = f'[CQ:at,qq={session.ctx["user_id"]}]' if config.welcome.at_menber else ""
            msg += config.welcome.msg
        print(session.ctx)
        await session.send(msg)


@on_request
async def _(session: RequestSession):
    logger.info('有新的请求事件：%s', session.ctx)


# 将函数注册为群请求处理器
@on_request('group')
async def _(session: RequestSession):
    if session.ctx['sub_type'] == 'invite':
        with SessionManager() as db_session:
            Group(group_number=session.ctx['group_id']).save(session=db_session)
        await session.approve()
        return

    # 判断验证信息是否符合要求
    if session.ctx['comment'] == '咕咕咕':
        # 验证信息正确，同意入群
        await session.approve()
        return
    # 验证信息错误，拒绝入群
    await session.reject('验证信息错误，拒绝入群')


# 将函数注册为群请求处理器
@on_request('friend')
async def _(session: RequestSession):
    # 判断验证信息是否符合要求
    if session.ctx['comment'] == '咕咕咕':
        # 验证信息正确，同意入群
        await session.approve()
        return


@on_request('group_decrease')
async def _(session: RequestSession):
    if session.ctx['sub_type'] == 'kick_me':
        with SessionManager() as db_session:
            Group.first(session=db_session, group_number=session.ctx['group_id']).delete(session=db_session)
