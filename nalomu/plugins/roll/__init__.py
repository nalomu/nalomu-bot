__plugin_name__ = '摇号'
__plugin_usage__ = r"""
roll/摇号/摇 [MAX=100] [MIN=0] 获取一个随机数字
    MAX 最大值 默认100
    MIN 最小值 默认0
    顺序无所谓
""".strip()
from .RollCommands import *
