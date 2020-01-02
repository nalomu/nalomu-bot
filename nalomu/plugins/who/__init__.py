from nonebot import on_command, CommandSession
from nonebot import on_natural_language, NLPSession, IntentCommand

from .data_source import get_self_info


@on_command('who', aliases=('你是', '你是谁', '你妈妈是谁'))
async def who(session: CommandSession):
    info = await get_self_info()
    await session.send(info)


# on_natural_language 装饰器将函数声明为一个自然语言处理器
# keywords 表示需要响应的关键词，类型为任意可迭代对象，元素类型为 str
# 如果不传入 keywords，则响应所有没有被当作命令处理的消息
@on_natural_language(keywords={'谁', '爸爸'})
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    return IntentCommand(69.0, 'who')
