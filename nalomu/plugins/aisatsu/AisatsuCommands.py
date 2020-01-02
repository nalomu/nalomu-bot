import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, DefaultDict, Optional, Set

from nonebot import NLPSession, IntentCommand, CommandSession

from nalomu.commands import BaseCommand, method_command
from nalomu.commands.functions import method_nlp

RegexType = type(re.compile(''))


class AisatsuConstruct:
    def __init__(self, last_send_msg='', last_send_user=None, last_send_time=None):
        self.last_send_msg: Optional[str] = last_send_msg
        self.last_send_user: Optional[int] = last_send_user
        self.last_send_time: Optional[datetime] = last_send_time

    def check_and_update(self, aisatsu_type, user_id):
        if (((self.last_send_msg != aisatsu_type)
             and (self.last_send_user != user_id))
                or (datetime.now() - self.last_send_time > timedelta(minutes=1))):
            self.last_send_msg = aisatsu_type
            self.last_send_user = user_id
            self.last_send_time = datetime.now()
            return True
        return False


class RepeatConstruct:
    def __init__(self, repeat_msg='', repeat_users: List[int] = None, repeat_time=None):
        self.repeat_msg: Optional[str] = repeat_msg
        self.repeat_users: Optional[List[int]] = repeat_users or []
        self.repeat_times: Optional[datetime] = repeat_time


class Aisatsu:
    keys: Set[str] = set()
    aisatsus: Set['Aisatsu'] = set()

    def __init__(self, key, keywords, message):
        self.key: str = key
        self.regex: RegexType = re.compile(f"({'|'.join(keywords)})")
        self.message: str = message
        self.aisatsus.add(self)
        self.keys.add(self.key)

    def __repr__(self):
        return f"<Aisatsu key:{self.key},regex:{self.regex},message:{self.message}>"

    @classmethod
    def get(cls, key) -> 'Aisatsu':
        return next((aisatsu for aisatsu in cls.aisatsus if aisatsu.key == key), None)


class AisatsuCommands(BaseCommand):
    plugin_name = '打招呼'
    aisatsu_dict: DefaultDict[str, AisatsuConstruct] = defaultdict(AisatsuConstruct)
    repeat_dict: DefaultDict[str, RepeatConstruct] = defaultdict(RepeatConstruct)

    @method_command('aisatsu')
    async def aisatsu(self):
        """
当你发早上好，午好，晚上好，可爱，晚安等的时候bot会跳出来跟你打招呼
同一句话bot在1分钟之内不会发两次
同一个用户的不同关键词1分钟内也不会触发bot
私聊除外
        """
        assert isinstance(self.session, CommandSession)
        aisatsu_type = self.get('type', required=False)
        if aisatsu_type not in Aisatsu.keys:
            return
        aisatsu: Aisatsu = Aisatsu.get(aisatsu_type)
        if not self.group_id:
            # 私聊
            await self.send(aisatsu.message)
            return
        else:
            # 群聊
            group_aisatsu = self.aisatsu_dict[self.group_id]
            if group_aisatsu.check_and_update(aisatsu_type, self.user_id):
                await self.send(aisatsu.message)

    @method_command("repeat")
    async def repeat(self):
        """
人的本质就是复读机，bot也是
当一句话被两个人重复之后bot也会跟着重复
        """
        msg = self.get('msg')
        await self.send(msg)

    @method_nlp(only_to_me=False)
    async def _(self):
        assert isinstance(self.session, NLPSession)
        _ = self.check_repeat()
        if _:
            return _
        _ = self.check_aisatsu()
        if _:
            return _

    def check_repeat(self):
        stripped_msg = self.stripped_msg
        if self.group_id:
            group_id = self.group_id
            user_id = self.user_id
            group_repeat: RepeatConstruct = self.repeat_dict[group_id]
            if group_repeat.repeat_msg != stripped_msg:
                group_repeat.repeat_msg = stripped_msg
                group_repeat.repeat_times = 1
                group_repeat.repeat_users = [user_id]
            else:
                if user_id not in group_repeat.repeat_users:
                    group_repeat.repeat_times += 1
                    group_repeat.repeat_users.append(user_id)
                    if group_repeat.repeat_times == 2:
                        return IntentCommand(100, 'repeat', args={"msg": stripped_msg})

    def check_aisatsu(self):
        for _ in Aisatsu.aisatsus:
            if _.regex.search(self.stripped_msg):
                return IntentCommand(100, 'aisatsu', args={"type": _.key})


Aisatsu(key='nya',
        keywords=['(^喵[~]?$)'],
        message='喵')
Aisatsu(key='ohayou',
        keywords=['ohayou', '早(上)?(好|安)', '(^早$)', 'おはよう'],
        message='早上好！')
Aisatsu(key='konnichiwa',
        keywords=['konnichiwa', '(中)?午[好安]', 'こんにちわ'],
        message='安好')
Aisatsu(key='konbanwa',
        keywords=['konbanwa', '晚(上)?好', 'こんばんは'],
        message='晚上好!')
Aisatsu(key='kawaii',
        keywords=['kawaii', '可[爱愛]', '卡哇伊', 'かわいい', 'カワイイ'],
        message='卡哇伊！')
Aisatsu(key='oyasumi',
        keywords=['oyasumi', '晚安', 'お(やす|休)み'],
        message='晚安~')
Aisatsu(key='hentai',
        keywords=['hentai', '变态', '変態', 'へんたい'],
        message='hentai！')
Aisatsu(key='gokigenyou',
        keywords=['gokigenyou', '([御ご]機嫌|ごきげん)よう'],
        message='安好')
Aisatsu(key='byebye',
        keywords=['bye', '拜拜', '白白', '挥挥', '再见', 'じゃあ', 'さよなら'],
        message='拜拜~')

__all__ = ['AisatsuCommands']
