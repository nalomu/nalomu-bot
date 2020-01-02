__plugin_name__ = '备忘录'
__plugin_usage__ = r"""
memorandum_list/备忘录 查看备忘录列表
memorandum_add/添加备忘录 [标题][##内容] (参数以两个#分隔)
memorandum_del/删除备忘录 [标题]
memorandum_del_all/清空备忘录
""".strip()

from .MemorandumCommands import *
