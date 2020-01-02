from .OtherCommands import *
__plugin_name__ = '其他'
__plugin_usage__ = rf"""
时间：发送“时间”获取当前时间（默认东京时间）
    现支持 {','.join(tzs.keys())}
    不嫌麻烦也可以 时间 + TIMEZONE
    TIMEZONE ：pytz中的时区

添加bot授权用户/add_super_user/asu
删除bot授权用户/del_super_user/dsu
""".strip()
