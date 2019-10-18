from Engine.engine_config import *
from game_config import *
# import os
#
# if os.path.isfile(CONFIG_OVERRIDE_ABSOLUTE):
#     import importlib.util
#
#     config_spec = importlib.util.spec_from_file_location('config', location=CONFIG_OVERRIDE_ABSOLUTE)
#     config_module = importlib.util.module_from_spec(config_spec)
#     config_spec.loader.exec_module(config_module)
#     config_dict = config_module.__dict__
#     config_builtins = config_module.__builtins__.keys()
#     globals().update({k: config_dict[k] for k in dir(config_module) if k not in config_builtins})
