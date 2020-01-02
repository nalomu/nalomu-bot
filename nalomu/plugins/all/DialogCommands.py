import difflib
import re
from datetime import datetime
from sre_constants import error as RegexError

from nonebot import get_bot, NLPSession, IntentCommand
from nonebot.command import call_command, CommandSession
from nonebot.command.argfilter import controllers
from nonebot.command.argfilter.validators import not_empty
from pytz import timezone

from nalomu.commands import BaseCommand, method_command
from nalomu.commands.functions import method_nlp, method_parser
from nalomu.orm import Dialog, SessionManager
from nalomu.plugins.user import NUser


def string_similar(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()


class DialogContract(object):
    def __init__(self, meta_msg, command: Dialog, base=30):
        self.command = command
        self.meta_msg = meta_msg
        self.result = command.result
        self.base = base
        self.string_similar_score = string_similar(self.meta_msg, self.command.command)
        self.matched_score = self.string_similar_score * (100 - base) + base


class DialogCommands(BaseCommand):
    plugin_name = "调教"

    @method_command('cant_understand', need_bot_open=True)
    async def cant_understand(self):
        """
        :not_usage:
        无命令时的缺省处理
        """
        await self.send('我不是很懂呢')

    @method_command('nani', need_bot_open=True)
    async def nani(self):
        """
        :not_usage:
        消息为空时的缺省处理
        """
        if not self.has_arg('_command'):
            await self.send('怎么辣', at_sender=True)
        command = self.get('_command')
        await call_command(get_bot(),
                           self.session.ctx,
                           'dialog_res',
                           args={'res': command})

    @method_command("dd_no_sleep")
    async def dd_no_sleep(self):
        """
        :not_usage:
        0-1点时的回应
        """
        pass
        # await session.send("在？臭dd不需要睡眠的🦄？")

    @method_command('dialog', aliases=('调教', '添加对话'), need_bot_open=True)
    async def dialog(self):
        """
        dialog/调教/添加对话 :添加新的对话 一次5积分
        """
        imu = '(' + '|'.join([
            '我家还[蛮挺]大的',
            '压力马斯内',
            '杰哥不要啊',
            '救世啊',
            '114514',
        ]) + ')'
        is_regex = self.has_arg('regex')
        user_qq = self.user_id
        nuser = await NUser.get(user_qq)
        if int(await nuser.point) <= 5:
            await self.send('积分不足', at_sender=True)
            return
        # 获取问题
        q: str = self.get('q', prompt='问题', arg_filters=[
            controllers.handle_cancellation(self.session),  # 处理用户可能的取消指令
            str.strip,  # 去掉两边空白字符
            not_empty('输入不能为空'),  # 不为空
        ])
        if re.search(imu, q) is not None:
            await self.send('？你好臭啊', at_sender=True)
            return
        if is_regex:
            try:
                re.compile(q.replace('\\', '\\\\'))
            except RegexError:
                await self.send('正则不合法', at_sender=True)
                return

        # 获取回答
        a = self.get('a', prompt='回答', arg_filters=[
            controllers.handle_cancellation(self.session),  # 处理用户可能的取消指令
            str.strip,  # 去掉两边空白字符
            not_empty('输入不能为空'),  # 不为空
        ])
        if re.search(imu, a) is not None:
            await self.send('？你好臭啊', at_sender=True)
            return

        # 查找是否已经有了
        with SessionManager() as db_session:

            res: Dialog = Dialog.first(session=db_session, command=q)
            if res is not None:  # 已经有了
                # 确认覆盖
                flag: str = self.get('_', prompt=f'已经有这条了，回答：{res.result}，要覆盖嘛？(y/n)')
                if flag.lower() == 'y':
                    res.command = q
                    res.result = a
                    res.user_id = nuser.nuid
                    res.is_regex = is_regex
                    res.save(session=db_session)
                    from nalomu.orm import UserPointLog
                    (await nuser.user).change_point(
                        change_point=-5,
                        desc='调教',
                        type_=UserPointLog.TypeEnum.chokyo
                    ).save(session=nuser.session)
                else:
                    await self.send('取消了', at_sender=True)
                    return
            else:  # 保存
                from nalomu.orm import UserPointLog
                Dialog(command=q,
                       result=a,
                       user_qq=nuser.nuid,
                       is_regex=is_regex).save(session=db_session)
                (await nuser.user).change_point(
                    change_point=-5,
                    desc='调教',
                    type_=UserPointLog.TypeEnum.chokyo
                ).save(session=nuser.session)

        await self.send('ok', at_sender=True)

    @method_command('dialog_res', need_bot_open=True)
    async def dialog_res(self):
        """
        :not_usage:
        如果在问题在表里有近似的回答就返回调教的结果
        没有就调用缺省回答
        :return:
        """
        # logger.info(session.state)
        res: str = self.get('res', required=False)
        # 已经处理过了，直接发送
        if res:
            if self.has_arg('run'):
                await self.send(res)
            else:
                # 查找命令
                dialog = self.get_result(res)
                if dialog and dialog.matched_score >= 75:  # 分数足够
                    await self.send(dialog.result)
                else:
                    await call_command(get_bot(), self.session.ctx, 'cant_understand')

    @staticmethod
    def get_result(message: str) -> DialogContract:
        # full matched
        with SessionManager() as session:
            full_matched_command = Dialog.first(session=session, command=message)
            if full_matched_command:
                return DialogContract(message, full_matched_command)


    @method_command('dialog_from', aliases=('dfrom', '查找对话',))
    async def dialog_from(self):
        """
        dialog_from/dfrom/查找对话 [问题] :查找对话相关信息
        """
        command = self.get('command', prompt="问题")
        info: DialogContract = self.get_result(command)
        await self.send(
            f"""搜索词：{info.meta_msg}
    qq: {info.command.user.qq}
    问题：{info.command.command}
    回答：{info.result}
    是否是正则匹配：{['否', '是'][info.command.is_regex]}
    相似度：{info.string_similar_score}
    基数：{info.base}
    匹配得分（大于等于60才会回答）：{info.matched_score}
    时间：{info.command.updated_at.strftime('%Y-%m-%d %H:%M:%S')}"""
            if info else "没有找到，可能没有录入", no_delay=True)

    @dialog.args_parser
    @method_parser
    async def _(self):
        assert isinstance(self.session, CommandSession)
        current_arg = self.session.current_arg
        if self.session.is_first_run:
            if current_arg in {'-r', '--regex'}:
                self.session.state['regex'] = True
            return

        self.session.state[self.session.current_key] = current_arg

    @dialog_from.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('command', no_pause=True)

    @method_nlp(only_short_message=False)
    async def _(self):
        return IntentCommand(60.0, 'cant_understand')

    @method_nlp(only_short_message=False)
    async def _(self):
        # 去掉消息首尾的空白符
        stripped_msg = self.stripped_msg

        # 查找是否在字典里

        dialog: DialogContract = self.get_result(stripped_msg)
        if dialog:
            # 字数多了之后很容易超过100
            return IntentCommand(dialog.matched_score, 'dialog_res', args={'res': dialog.result, 'run': True})

    @method_nlp(allow_empty_message=True, only_short_message=False)
    async def _(self):
        assert isinstance(self.session, NLPSession)
        if datetime.now(timezone('Asia/Shanghai')).hour < 1:
            return IntentCommand(1000, "dd_no_sleep")
        stripped_msg = self.stripped_msg
        if stripped_msg == '' or re.search('^[~,，.。\\\\/!！…、]$', stripped_msg):
            return IntentCommand(100, 'nani')


__all__ = ['DialogCommands']
