import nonebot
from nonebot.argparse import ArgumentParser

from .data_source import YoudaoFanyi

__plugin_name__ = '翻译'
__plugin_usage__ = r"""
翻译

使用方法：
    translate [OPTIONS] CONTENT
    翻译 [OPTIONS] CONTENT

OPTIONS：
    -h, --help  显示本使用帮助
CONTENT：
    要翻译的内容
""".strip()


@nonebot.on_command('translate', aliases=('翻译',), shell_like=True)
async def translate(session: nonebot.CommandSession):
    parser = ArgumentParser(session=session, usage=__plugin_usage__)
    parser.add_argument('content')
    args = parser.parse_args(session.argv)
    try:
        tr = '\n'.join([line["tgt"] for line in await YoudaoFanyi().fanyi(str(args.content))])
        await session.send(tr)
    except Exception as e:
        nonebot.logger.error(e)
        await session.send('出错啦！')
