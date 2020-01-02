import os

from aiocqhttp import ApiNotAvailable
from quart import Quart, jsonify, request, send_from_directory


from nalomu import NDict, send_msg_to_user
from nalomu.config_loader import config


def init_http_api(app: Quart):
    @app.route('/data/<path:path>')
    async def send_dat(path):
        from config import APP_ROOT
        return await send_from_directory(os.path.join(APP_ROOT, 'nalomu/data'), path)
