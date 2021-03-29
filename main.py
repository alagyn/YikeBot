# main.py
# Main executable for YikeSnake

import os
import sys
from dotenv import load_dotenv
import time

import yikeSnake
import consts

if __name__ == "__main__":
    load_dotenv()
    token = os.getenv('DISCORD_TOKEN')
    debug = os.getenv('DEBUG')
    backupFolder = os.getenv('BACKUP_LOC')

    if debug == '0':
        logId = time.strftime("M%m_D%d_Y%Y_%H-%M-%S")
        logFile = f'./logs/adminLogs/{logId}.log'
        waitTime = consts.DEF_WAIT_TIME
        sys.stderr = open(f'./logs/errorLogs/err_{logId}.log', mode='w')
        backupTime = consts.DEF_BACKUP_TIME
    else:
        logFile = None
        waitTime = consts.DEBUG_WAIT_TIME
        backupTime = consts.DEBUG_BACKUP_TIME

    curBot = yikeSnake.YikeSnake(logFile=logFile, waitTime=waitTime, backupTime=backupTime, backupFolder=backupFolder)

    curBot.load_extension('cmds.admin')
    curBot.load_extension('cmds.yike')
    curBot.load_extension('cmds.quote')

    curBot.load_extension('cmds.util')
    curBot.load_extension('cmds.music.music')
    # curBot.load_extension('cmds.music-reference')

    curBot.run(token)

    sys.exit(0)
