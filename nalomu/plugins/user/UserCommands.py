import re

from nonebot import IntentCommand, CommandSession

from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp
from nalomu.util import is_number
from .data_source import NUser, fortune_list, fortune_list_image


class UserCommands(BaseCommand):
    def __init__(self, session: CommandSession):
        super().__init__(session)
        self.user = NUser(session.ctx['user_id'])

    @method_command('set_name', aliases=('我是', '我叫',))
    async def set_name(self):
        name = self.get('name', prompt='你想让我怎么称呼你？')
        res = await self.user.set_name(name)
        await self.send('ok, 我记住啦' if res else '好像出错了哦')

    @set_name.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('name')

    @method_command('get_name', aliases=('我是谁？', '我叫什么？',))
    async def get_name(self):
        name = await self.user.name
        msg = '是{}，对吧？'.format(name) if name else '还没有告诉我你的名字哦'
        await self.send(msg)

    @method_command('switch_gmf', aliases=('切换早安开关',))
    async def set_gmf(self):
        res = await self.user.set_gmf()
        await self.send('开' if res else '关')

    @method_command('switch_gnf', aliases=('切换晚安开关',))
    async def set_gmf(self):
        res = await self.user.set_gnf()
        await self.send('开' if res else '关')

    @method_command('checkin', aliases=('签到', '簽到'), only_to_me=False)
    async def checkin(self):
        res = await self.user.checkin()
        if res is not False:
            if is_number(res):
                await self.send('签到成功~')
                await self.send_image(fortune_list_image[int(res)])
                return
            else:
                msg = f'签到成功，今日运势：{res}, {fortune_list[res]}(随机抽取，仅供参考)'
        else:
            msg = f'已经签到过了'
        await self.send(msg, at_sender=True)

    @method_command('bonus', aliases=('连签奖励',))
    async def bonus(self):
        res = await self.user.bonus()
        msg = "连签奖励：{}积分，最高连签奖励：{}积分".format(res['normal'], res['highest'])
        await self.send(msg)

    @method_command('musubitsuke', aliases=('绑签',))
    async def musubitsuke(self):
        res = await self.user.musubitsuke()
        msgs = ("绑签成功，祝你好运~", "已经绑过了", "还没有签到过")
        await self.send(msgs[res])

    @method_command("Today's fortune", aliases=('今日运势', '运势', '運勢'), only_to_me=False)
    async def todays_fortune(self):
        (is_checkin, fortune) = await self.user.fortune
        if is_number(fortune):
            await self.send_image(fortune_list_image[int(fortune)])
        else:
            msg = f'今日运势：{fortune}, {fortune_list[fortune]}(随机抽取，仅供参考)'
            await self.send(msg, at_sender=True)
        if is_checkin:
            await self.send('顺手签到成功~~~积分+10', at_sender=True)

    @method_command('check_point', aliases=('查看积分', '积分'))
    async def check_point(self):
        point = await self.user.point
        await self.send(f'积分：{point}')

    @method_command('continuous_checkin', aliases=('连签', '连续签到', '连续签到天数'), only_to_me=False)
    async def continuous_checkin(self):
        continuous_days = await self.user.continuous_checkin
        await self.send(f'连续签到天数：{continuous_days}')

    @method_command('high_continuous_checkin', aliases=('u_hcc', '最高连签', '最高连续签到', '最高连续签到天数'), only_to_me=False)
    async def high_continuous_checkin(self):
        u_hcc = await self.user.hcc
        await self.send(f'最高连续签到天数：{u_hcc}')

    @method_command('slap', aliases=('鼓掌',))
    async def slap(self):
        res = await self.user.slap()
        from config import NICKNAME
        msg = f'啪啪啪啪啪啪({NICKNAME[0]}为你献上了热烈的掌声并且积分-1)' if res else '积分不足'
        await self.send(msg)

    @method_nlp(keywords={'我叫', '我是'})
    async def _(self):
        # 去掉消息首尾的空白符
        stripped_msg = self.stripped_msg
        if re.search('[?？谁]', stripped_msg, re.M | re.I) is not None:
            return IntentCommand(85.0, 'get_name')
        print(stripped_msg)
        stripped_msg = re.sub('我[是叫]', '', stripped_msg)

        # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
        return IntentCommand(85.0, 'set_name', current_arg=stripped_msg or '')

    @method_nlp(keywords={'运势', '運勢'})
    async def _(self):
        # 返回意图命令，前两个参数必填，分别表示置信度和意图命令名
        return IntentCommand(90.0, "Today's fortune")


__all__ = ['UserCommands']
