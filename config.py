from os import path

from nonebot.default_config import *
from nalomu.config_loader import config as file_config

HOST = file_config.server.host
PORT = file_config.server.port
SUPERUSERS = file_config.super_user
COMMAND_START = {'', '/', '!', '／', '！'}
NICKNAME = file_config.nickname
ROOT = path.dirname(path.realpath(__file__))
BOT_SWITCH = True
APP_ROOT = path.abspath(path.dirname(__file__))
DATA_ROOT = path.join(APP_ROOT, 'nalomu/data')
TEMPLATES_ROOT = path.join(APP_ROOT, 'nalomu/templates')
if file_config.using_docker:
    DATA_URL = f'http://{file_config.server.host}:{file_config.server.port}/data'
else:
    DATA_URL = f"file://{DATA_ROOT}"
