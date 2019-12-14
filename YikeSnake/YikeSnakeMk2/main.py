# main.py
# Main executable for YikeSnake

import os
import sys
from dotenv import load_dotenv
import time

import yikeSnake
import consts

load_dotenv()
token = os.getenv('DISCORD_TOKEN')
debug = os.getenv('DEBUG')

if debug == '0':
    logId = time.strftime("M%m_D%d_Y%Y_%H-%M-%S")
    logFile = f'./logs/adminLogs/{logId}.log'
    waitTime = consts.DEF_WAIT_TIME
    sys.stderr = open(f'./logs/errorLogs/err__{logId}.log', mode='w')
else:
    logFile = None
    waitTime = consts.DEBUG_WAIT_TIME

curBot = yikeSnake.YikeSnake(logFile=logFile, waitTime=waitTime)

curBot.load_extension('cmds.admin')
curBot.load_extension('cmds.yike')
curBot.load_extension('cmds.quote')
curBot.load_extension('cmds.util')

curBot.run(token)
