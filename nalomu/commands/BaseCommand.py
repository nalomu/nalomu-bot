from typing import Optional, List, Dict

from nonebot import CommandSession, NLPSession, NoticeSession
from nonebot.command import Command
from nonebot.session import BaseSession
from nonebot.typing import Message_T, Filter_T

from nalomu import send_msg_auto_delay, NDict


class BaseCommand:
    plugin_name = None

    def __init__(self, session: BaseSession):
        self.session = session
        self.group_id = session.ctx['group_id'] if 'group_id' in session.ctx else None
        self.user_id = session.ctx['user_id']
        if isinstance(self.session, CommandSession):
            self.stripped_msg = self.session.current_arg_text.strip()
            self.images = self.session.current_arg_images
        elif isinstance(self.session, NLPSession):
            self.stripped_msg = self.session.msg.strip()
            self.images = self.session.msg_images

    async def send(self, msg, at_sender=False, no_delay=False):
        if not no_delay:
            await send_msg_auto_delay(self.session.ctx, msg, at_sender)
        else:
            await self.session.send(msg, at_sender=at_sender)

    def get(self, key: str, *,
            prompt: Optional[Message_T] = None,
            arg_filters: Optional[List[Filter_T]] = None,
            required=True,
            **kwargs):
        func_get_args = locals()
        func_get_args.pop('self')
        func_get_args.pop('required')
        func_get_args.pop('kwargs')
        func_get_args.update(kwargs)
        assert isinstance(self.session, CommandSession)
        if required:
            return self.session.get(**func_get_args)
        else:
            return NDict(self.session.state).get(key)

    def has_arg(self, key):
        assert isinstance(self.session, CommandSession)
        return key in self.session.state.keys()

    def parse_image(self, key):
        assert isinstance(self.session, CommandSession)
        image = self.images

        if self.session.is_first_run:
            if len(image) > 0:
                self.session.state[key] = image
            return
        if self.session.current_key == key:
            if len(image) == 0:
                self.session.pause('请发送图片')
            self.session.state[key] = image

    def parse_striped_text(self, key, msg='', no_pause=False):
        assert isinstance(self.session, CommandSession)
        stripped_msg = self.stripped_msg
        if self.session.is_first_run:
            if stripped_msg:
                self.session.state[key] = stripped_msg
            return
        if self.session.current_key == key:
            if not stripped_msg and not no_pause:
                self.session.pause('请发送' if not msg else msg)
            self.session.state[key] = stripped_msg

    async def send_image(self, img_url, no_cache=False):
        await self.send(f'[CQ:image{",cache=0" if no_cache else ""},file={img_url}]', no_delay=True)

    @classmethod
    def get_usage(cls) -> Dict:
        """
        从类中获取使用了method_command装饰器的方法的注释作为帮助
        不获取以:not_usage:开头的doc
        :return: 获取到的帮助
        """
        usages = {}
        for funcname in cls.__dict__:
            func = getattr(cls, funcname)
            if hasattr(func, 'is_command') and getattr(func, 'is_command'):
                doc: str = func.__doc__.strip()
                if doc and not doc.startswith(':not_usage:'):
                    usages[funcname] = doc
        return usages


__all__ = ["BaseCommand"]
