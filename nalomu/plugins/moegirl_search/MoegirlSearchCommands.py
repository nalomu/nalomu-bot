from mediawiki import MediaWiki
from nonebot import IntentCommand, logger

from nalomu.commands import BaseCommand, method_command, method_parser, method_nlp


class MoegirlSearchCommands(BaseCommand):
    @method_command('moegirl_search', aliases=('萌娘百科', '萌百'))
    async def moegirl_search(self):
        q = self.get('query', prompt='要找什么？')
        try:
            res = await self.moegirl_search(q)
            await self.send(res if res else "没有找到;w;")
        except Exception as e:
            logger.error(e)
            await self.send('出错啦！')

    @moegirl_search.args_parser
    @method_parser
    async def _(self):
        self.parse_striped_text('query')

    @method_nlp(keywords={'萌娘百科'})
    async def _(self):
        stripped_msg = self.stripped_msg
        return IntentCommand(90.0, 'moegirl_search', current_arg=stripped_msg.replace('萌娘百科', '') or '')

    @staticmethod
    async def moegirl_search(q):
        moegirlwiki = MediaWiki(url='http://zh.moegirl.org/api.php')
        t = moegirlwiki.search(q)
        if len(t) == 0:
            return False
        p = moegirlwiki.page(t[0])
        return p.summary


__all__ = ['MoegirlSearchCommands']
