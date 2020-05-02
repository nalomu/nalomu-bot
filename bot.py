#!/usr/local/bin/python3.6
# -*- coding: UTF-8 -*-
import argparse
import os
import sys
from os import path

import nonebot
import config

from daemon import Daemon
from nalomu.config_loader import config as localconfig
from nalomu.http_api import init_http_api


class BotDaemon(Daemon):
    def run(self):
        sys.stdout.write('Daemon started with pid {}\n'.format(os.getpid()))
        self.real_run()

    @staticmethod
    def real_run():
        nonebot.init(config)
        nonebot.load_plugins(
            path.join(config.ROOT, 'nalomu', 'plugins'),
            'nalomu.plugins'
        )
        nonebot.load_builtin_plugins()
        init_http_api(nonebot.get_bot().server_app)
        nonebot.run()


if __name__ == '__main__':
    PIDFILE = '/tmp/bot.pid' if not localconfig.pid_file else localconfig.pid_file
    LOG = '/tmp/nalomu_nonebot.log' if not localconfig.log_file else localconfig.log_file

    parser = argparse.ArgumentParser(description='运行bot')
    parser.add_argument('--run', action='store_true', help='直接运行')
    parser.add_argument('--start', action='store_true', help='运行')
    parser.add_argument('--stop', action='store_true', help='停止')
    parser.add_argument('-r', '--restart', action='store_true', help='重启')
    args = parser.parse_args()
    print(args)
    daemon = BotDaemon(pidfile=PIDFILE, stdout=LOG, stderr=LOG, )
    if args.run:
        BotDaemon.real_run()
    elif args.start:
        daemon.start()
    elif args.stop:
        daemon.stop()
    elif args.restart:
        daemon.restart()
    else:
        parser.print_help()
        raise SystemExit(1)
