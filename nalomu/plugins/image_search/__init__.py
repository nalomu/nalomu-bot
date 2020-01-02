__plugin_name__ = '搜图'
__plugin_usage__ = r"""
image_search/搜图
    -a --ascii2d 使用ascii2d搜索
    -b --book 启用搜索本子，仅私聊可用（不一定搜得到）
""".strip()
from .ImageSearchCommands import *
