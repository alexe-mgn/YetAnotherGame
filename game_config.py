from Engine.engine_config import *

APP_NAME = r'Yet Another Game'
CODE_APP_NAME = transform_name(APP_NAME)
EXCEPTION_FILE = '%s_traceback.txt' % (CODE_APP_NAME,)
RECORDS_FILE = 'Game\\storage\\game_results.json'


class CHANNEL(NameSpace):
    PLASMA_WEAPON = 0
    PULSON_WEAPON = 1
    PULSON_EXPLOSION = 2
    NET_WEAPON = 3
    MINI_LAUNCH = 4
