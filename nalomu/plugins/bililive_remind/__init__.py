__plugin_name__ = '开播提醒'
__plugin_usage__ = r"""
暂时开启，将时间延长至1分钟1次

每半分钟检查一次监听的房间是否开播
简写/中文全写/英文全写
alr/添加监听的房间/add_live_remind [ROOM_ID]
dlr/删除监听的房间/del_live_remind [ROOM_ID]
lll/查看监听的房间/live_listen_list [ROOM_ID] 
ROOM_ID 房间id，可以是短id
""".strip()

from .NBiliBiliLive import NBiliBiliLive
from .BiliRemind import BiliRemind
from . import LiveCommands
