import nonebot
from nonebot import logger

from nalomu.commands import ImageCommand, method_command


def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]


class UsageCommands(ImageCommand):

    @method_command('usage', aliases=['使用帮助', '帮助', '使用方法', '食用方法', '功能列表'])
    async def usage(self):
        # 获取设置了名称的插件列表
        plugins = list(filter(lambda p: p.name, nonebot.get_loaded_plugins()))
        arg = self.stripped_msg.lower()
        plugin = next((p for p in plugins if p.name == arg), False)
        logger.info(plugin)
        await self.send(self.render_image('usage', plugins=plugins, plugin=plugin))
